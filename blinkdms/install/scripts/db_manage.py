# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
script for CLI execution
- create new BLINKDMS database schema from dumps

# create new database ...
export PYTHONPATH=/opt/blinkdms
python3 /opt/blinkdms/blinkdms/install/scripts/db_manage.py --create --dbuser "blk_dev" --dbuser_pw "jsHGj23456xXPL"

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

_logarr=[]
def _log(text):
    _logarr.append(text)

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
        
        _log("_exec_sql_raw: CMD:" + os_cmd)
        if self.simulation:
            _log("SIMULATION: no execution"  ) 
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
        
        _log( "DEBUG:_exec_sql: output:" + str(outs) + ' err:'+str(errs_str) )    
    
    def exec_sqlfile(self, filename, user):
        
        print ("DEBUG:_exec_sqlfile: filename:" + filename + ' user:'+user )
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
    
    def __init__(self, db_user):
        
        self.db_user = db_user
        self.tablespace = dbuser+'_tab'
        self.db_name='dmsdb'
        
        self.infox = {}
        
        self.db_sql_src = '/opt/blinkdms/blinkdms/install/sql'
        
        self.sql_lib = Sql_perform()
        # self.sql_lib.simulation = 1
       
        
    def crea_user(self):
        
               
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

    def create(self, crea_option):
        
        #db_user    = self.db_user
        #tablespace = self.tablespace
        
        self.db_pw = crea_option['dbuser_pw']
        
        self.infox['dbuser_pw'] = self.db_pw
        
        self.crea_user()
        self.import_db()
        #self.db_get_obj() # init user database handle
        #self.dirs_create()
        #self.import_post_actions()        
    
    def get_DB_infox(self):
        return self.infox
    
   
    def dirs_delete():
        pass
    
if __name__ == "__main__":
    
    # Create the parser
    my_parser = argparse.ArgumentParser(description='BlinkDMS database Manager: Create a new copy of a database')
    
    print (str(sys.argv) )
    
    my_parser.add_argument('--dbuser',  
                           type=str,
                           help='DB-user Name')
    
    my_parser.add_argument('--dbuser_pw',  
                           type=str,
                           help='DB-user-Password')      
    
    
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
    
   
    dbuser = args.dbuser
    dbuser_pw = args.dbuser_pw
    
    action = ''
    action_opt = ''
    need_customer_params = 1
    crea_option = {}
    
  
   
    if args.create:
        print('Create INSTANCE!.')
        action = 'new'     
        
    if args.delete:
        print('Delete INSTANCE!.')  
        action = 'delete' 

   
    if action=='' :
        print('Error: Please select an action!')
        sys.exit()        
        
    if action=='new':

        if not dbuser:
            print('ERROR: dbuser not given.')
            sys.exit() 
            
        if not dbuser_pw:
            print('ERROR: dbuser_pw not given.')
            sys.exit() 
            
    if action=='delete':

        if not dbuser:
            print('ERROR: dbuser not given.')
            sys.exit() 

        
    try:
        
        print('Action: '+action)
        db_mng_lib = Manage_DB(dbuser)
        
        if action =='new':
            crea_option['dbuser']=dbuser
            crea_option['dbuser_pw']=dbuser_pw
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
        
    print ("")
    print ("---------------------------------------------------")
    print ("INFOS:")
    for row in _logarr:
        
        print("- "+str(row))