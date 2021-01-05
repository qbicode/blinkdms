# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
script for CLI execution
- create new BLINKDMS database schema from dumps
- requirements: conf.py must exist with 'db' entry
- OLD params: --dbuser "blk_dev" --dbuser_pw "jsHGj23456xXPL"

# create new database ...
export PYTHONPATH=/opt/blinkdms
python3 /opt/blinkdms/blinkdms/install/scripts/db_manage.py --create --config_entry "dev" --app_root_pw "XXX"
python3 /opt/blinkdms/blinkdms/install/scripts/db_manage.py --delete --dbuser "blinkdms" 

File:           db_manage.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""



import os
import sys
import traceback
import subprocess

import argparse

from blinkdms.code.lib.f_utilities import BlinkError
from blinkdms.code.lib.db import db
from blinkdms.code.lib.oDB_USER import oDB_USER

try:
    from blinkdms.conf import config
except:
    print('ERROR: Please create the file blinkdms/conf/config.py first !')
    sys.exit()      

_logarr=[]

VERBOSE_LEVEL=0

def _log(text, min_level=0):
    
    if min_level>VERBOSE_LEVEL:
        return
    
    print("INFO: "+text)
    
def _help():
    print('This is the BlinkDMS database Manager: Create a new copy of a database.')
    print('Prerequisites:') 
    print('  - set blinkdms/conf/config.py ==> entry "db" for your database.')  
    print('Call:')
    print('python db_manage.py --create --config_entry "main" --app_root_pw "XXX" ')
    print('python db_manage.py --delete --dbuser "blinkdms" ')

class Sql_perform:
    
    simulation=0
    
    def _exec_sql_raw(self, substr, user=''):
        '''
        :param string user: database user
            if '': perform as DB-root
        '''

        # psql
        #   -b --echo-errors        echo failed commands
        os_cmd = '/bin/su -c  "psql -v ON_ERROR_STOP=1 -b -d dmsdb '
        if user!='':
            os_cmd = os_cmd + '-U '+user+' '
            
        os_cmd = os_cmd + substr + '" - postgres '
        
        _log("_exec_sql_raw: CMD:" + os_cmd, 1)
        if self.simulation:
            _log("SIMULATION: no execution", 1  ) 
            return        

        
        proc = subprocess.Popen(os_cmd, shell=True, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            outs, errs = proc.communicate(timeout=160)
        except TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()

        errs_str=''
        if len(errs):
            errs_str = errs.decode()
            raise ValueError ('SQL-Error: '+errs_str)
        
        _log( "DEBUG:_exec_sql: output:" + str(outs) + ' err:'+str(errs_str), 1 )    
    
    def exec_sqlfile(self, filename, user):
        
        _log( "_exec_sqlfile: filename:" + filename + ' user:'+user, 1 )
        substr = ' < ' +  filename       
        self._exec_sql_raw(substr, user)
     
    
    def exec_sql(self, sql_cmds, user=''):
        
        substr = '<<EOF' + "\n"
        sql_cmds = ["set client_min_messages = WARNING;"] + sql_cmds
        
        for onecmd in sql_cmds:
            substr = substr +  onecmd  + "\n" 
        
        substr = substr + 'EOF'         
        
        self._exec_sql_raw(substr, user)     


class Manage_DB:
    
    _db_obj = None
    infox= {}
    
    def __init__(self, db_user):
        
        self.db_user = db_user
        self.tablespace = dbuser+'_tab'
        self.db_name='dmsdb'
        
        self.infox = {}
        
        self.db_sql_src = '/opt/blinkdms/blinkdms/install/sql'
        
        self.sql_lib = Sql_perform()
        
        self.simulation = 0
        self._verbose   = 0
        # self.sql_lib.simulation = 1
    
    def verbose(self,verbose_flag):
        self._verbose = verbose_flag
    
    def db_get_obj(self):
        '''
        connect to new database as normal user
        create current DB_OBJ
        '''
        
        if self._db_obj:
            return self._db_obj
        
        config_entry = self.infox['config_entry']
        if config_entry=='':
            raise BlinkError(1, 'Need config_entry.') 
        
        if config_entry not in config.superglobal['db']:
            raise BlinkError(2, 'Need entry for "'+config_entry+'" in conf.py: superglobal["db"] .')      
        
        access_config = config.superglobal['db'][config_entry]
        
        self._db_obj = db(0)
        self._db_obj.open( access_config )
    
        return  self._db_obj        
        
    def crea_user(self):
        
        _log('create database user + tablespace..')
               
        pw =  self.db_pw
        if pw=='':
            raise BlinkError(1,'DB-User-Password needed')
        db_user = self.db_user
        tablespace = self.tablespace
        db_name = self.db_name

        
        sql_cmds=[]
        sql_cmds.append("create user "+db_user+" with password '"+pw+"';")
        sql_cmds.append("grant all privileges on database "+db_name+" to "+db_user+";")
        sql_cmds.append("CREATE SCHEMA "+tablespace+" AUTHORIZATION "+db_user+";")
        sql_cmds.append("ALTER SCHEMA "+tablespace+" OWNER TO "+db_user+";")
        sql_cmds.append("alter role "+db_user+" set search_path = "+tablespace+", pg_catalog;")
        
        self.sql_lib.exec_sql(sql_cmds)     
        
        
    def import_db(self):
        
        _log('import the database schema + initial data.')
        
        db_user = self.db_user
        # tablespace = self.tablespace
        db_sql_src = self.db_sql_src

        schema_file_short ='schema_dump.sql'

        data_file = os.path.join(db_sql_src, schema_file_short)
        self.sql_lib.exec_sqlfile(data_file, db_user)    
        
    def drop_user(self):
        
        _log('... DROP user '+ self.db_user )  
        sql_cmds=[]
        sql_cmds.append("DROP SCHEMA "+self.tablespace+" cascade;")
        sql_cmds.append("REASSIGN OWNED BY "+self.db_user+" TO postgres;")
        sql_cmds.append("DROP OWNED BY "+self.db_user+";")
        sql_cmds.append("DROP USER "+self.db_user+";")
        
        self.sql_lib.exec_sql(sql_cmds)    

    def _import_post_actions(self):
        #
        # set root pw
        #
        
        _log('set password for application-user root.')
        
        if  self.infox['root.pw']=='':
            raise BlinkError(1,'No root password given.')        
        
        pw_hash = oDB_USER.Table.hash_pw( self.infox['root.pw'] )
        
        user_id = self._db_obj.col_val_where('DB_USER', {'NICK':'root'}, 'DB_USER_ID')
        if not user_id:
            raise BlinkError(1,'Could not find user "root" in DB!')
        
        args = {  
            'PASS_WORD': pw_hash, 
        }
        
        if self.simulation:
            pass
        else:  
            self._db_obj.update_row( 'DB_USER', {'DB_USER_ID': user_id }, args )         

    def create(self, crea_option):
        
        #db_user    = self.db_user
        #tablespace = self.tablespace
        
        self.db_pw = crea_option['dbuser_pw']
        
        self.infox['dbuser_pw'] = self.db_pw
        self.infox['config_entry'] = crea_option['config_entry']
        self.infox['root.pw'] = crea_option['root.pw']
        
        _log('Config-Entry: '+ self.infox['config_entry'] )
        _log('DB-User: '     + self.db_user )
        _log('root-password: ' + self.infox['root.pw'] )
   
        self.crea_user()
        self.import_db()
        
        self.db_get_obj() # init user database handle
        #self.dirs_create()
        
        self._import_post_actions()        
    
    def get_DB_infox(self):
        return self.infox
    
   
    def dirs_delete():
        pass
    
    
    
if __name__ == "__main__":
    
    # Create the parser
    help_str = \
    'This is the BlinkDMS database Manager: Create a new copy of a database.' + "\n" + \
    'Prerequisites:'  + "\n" + \
    '  - set blinkdms/conf/config.py ==> entry "db" for your database.'  + "\n" + \
    'Call: ' + "\n" + \
    'python db_manage.py --create --config_entry "main" --app_root_pw "XXX" '  + "\n" + \
    'python db_manage.py --delete --dbuser "blinkdms" '  
    
    my_parser = argparse.ArgumentParser( description=help_str)
    
    print (str(sys.argv) )
    
    my_parser.add_argument('-v',  
                           action="store_true",
                           help='Verbose output')     
    
    my_parser.add_argument('--config_entry',  
                           type=str,
                           help='Config entry: superglobal["db"]: KEY ')    
    
    my_parser.add_argument('--dbuser',  
                           type=str,
                           help='DB-user Name')
    
    my_parser.add_argument('--dbuser_pw',  
                           type=str,
                           help='DB-user-Password')      
    
    my_parser.add_argument('--app_root_pw',  
                           type=str,
                           help='Password of application user root')    
    
    my_parser.add_argument('--delete',  
                           action="store_true",
                           help='Delete instance') 
    
  
    
    my_parser.add_argument('--create',  
                           action="store_true",
                           help='Create a new database')  
    
    
    
    args_list = sys.argv.copy()
    del(args_list[0])
    args_str = ' '.join(args_list)
    # Execute the parse_args() method
    args = my_parser.parse_args(args_list)
    
    config_entry = args.config_entry
    dbuser = args.dbuser
    dbuser_pw = args.dbuser_pw
    app_root_pw = args.app_root_pw
    verbose = 0
    
    action = ''
    action_opt = ''
    need_customer_params = 1
    crea_option = {}
    
    if args.v:
        print('Verbose!')
        verbose = 1 
        VERBOSE_LEVEL = 1
   
    if args.create:
        print('Create INSTANCE!.')
        action = 'new'     
        
    if args.delete:
        print('Delete INSTANCE!.')  
        action = 'delete' 

    
   
    if action=='' :
        print('Error: Please select an action!')
        sys.exit()  
        
    if config_entry!='' and config_entry is not None:

        if config_entry not in config.superglobal['db']:
            print('ERROR: Need entry for "'+config_entry+'" in conf.py: superglobal["db"] .')
            sys.exit()  
            
        db_entry  = config.superglobal['db'][config_entry]
        dbuser    = db_entry.get('user','')
        dbuser_pw = db_entry.get('password','')
          
        
    if action=='new':

        if not dbuser:
            print('ERROR: dbuser not given.')
            sys.exit() 
            
        if not dbuser_pw:
            print('ERROR: dbuser_pw not given.')
            sys.exit() 
            
        if not app_root_pw:
            print('ERROR: app_root_pw not given.')
            sys.exit()             
            
    if action=='delete':

        if not dbuser:
            print('ERROR: dbuser not given.')
            sys.exit() 

        
    try:
        
        print('Action: '+action)
        db_mng_lib = Manage_DB(dbuser)
        db_mng_lib.verbose(verbose)
        
        if action =='new':
            crea_option['dbuser']       = dbuser
            crea_option['dbuser_pw']    = dbuser_pw
            crea_option['root.pw']      = app_root_pw
            crea_option['config_entry'] = config_entry
            db_mng_lib.create(crea_option)
            
            infox = db_mng_lib.get_DB_infox()
            print ('- Created Database: '+str(infox) )
            
        if action =='delete':
            db_mng_lib.drop_user()
            # db_mng_lib.dirs_delete()
            
        
        
        
    except Exception as exc: 
        message   = str(exc)
        err_stack = traceback.extract_tb( exc.__traceback__ ) # tracebak of the exception
        print ("MAIN-ERROR:"+str(message) + "\nTRACE:" + str(err_stack) )
        
    else: 
        print ('OK')
        
        
    #if VERBOSE_LEVEL:
        
        #print ("")
        #print ("---------------------------------------------------")
        #print ("Detailed INFOS: (on -v)")
        #for row in _logarr:
            
            #print("- "+str(row))