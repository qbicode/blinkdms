# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
manage login

File:           login.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

import ldap3
import json
import time
import os


from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.f_utilities import BlinkError
from blinkdms.code.lib.init import initvars_cls
from blinkdms.code.lib.oDB_USER import oDB_USER
#from blinkdms.code.lib.oROLE import oROLE
#from blinkdms.code.lib import oUSER_PREF
from blinkdms.code.lib import oSYS_A_LOG
from blinkdms.conf  import config

class Blink_LDAP_Error(Exception):
    pass


class login:
    
    def __init__(self, session_obj):
        self.session_obj = session_obj
        self._mod_log=[]
        
    def get_log(self):
        return self._mod_log
    
    def _log(self, text):
        self._mod_log.append(text)
    
    @staticmethod
    def get_SW_version():
        #  read VERSION.txt
        
        filename = os.path.dirname(__file__) + '/../../VERSION.txt'
        fo = open(filename, 'r')
        line = fo.read().strip()
        fo.close()
         
        linearr = line.split(' ')
        version = linearr[0]
        
        return version
       

    
    def _log_fail(self, db_obj, username, failid, detail_text):
        '''
        :param failid: 
          1
          2
          3
          4
        :return: int do_lock
          0 : nothing
          1 : do_lock
        '''
        
        args = {
            'USER_NICK': username,
            'KEYX' :'LOGIN',
            'MESSAGE' : str(failid)+ ': ' +  detail_text  
        }
        oSYS_A_LOG.save_log(db_obj, args)
        
        do_lock = oSYS_A_LOG.ask_lock_user(db_obj, username)
        if do_lock:
            if username!='root':  
                oSYS_A_LOG.lock_user(db_obj, username)
                
        time.sleep(1) # extra penalty time for login fail to reduce login traffic
            
        return do_lock
        
    def check_verify(self, db_obj1, user_in, password_in):
        """
        can be used for LOGIN and SIGNING check
        :return:
          { 'status':1, 'user_id': DB_USER_ID, 'nick': username }
          
        except:
           1, "User or Password not valid.",
           6, "Too many tries for this login."
        """
        user_id  = 0
        username = user_in
        debug.printx(__name__, "username_in: '"+ username+"' "  )
         
        sql_cmd = "* from DB_USER where UPPER(NICK) like UPPER(" + db_obj1.addQuotes(username) + ")"
        db_obj1.select_dict(sql_cmd)
        if db_obj1.ReadRow():
            
            user_id  = db_obj1.RowData['DB_USER_ID'] 
            db_pw    = db_obj1.RowData['PASS_WORD'] 
            username = db_obj1.RowData['NICK']      # use NICK from DB ...
            login_deny = db_obj1.RowData['LOGIN_DENY']  
            login_method = db_obj1.RowData.get('LOGIN_METH','LOCAL')

        
        if not user_id:
            # user not exists
            do_lock = self._log_fail(db_obj1, username, 1, 'User not registered.')
            if  do_lock:
                raise BlinkError(6, "Too many tries for this login.", 'login')
            else:
                raise BlinkError( 1, "User or Password not valid.", 'login')
        
        if login_deny==2:
            # NO _log_fail action here ...
            # check, how long was lock before ...
            allow_again_inf = oSYS_A_LOG.ask_login_allow(db_obj1, username)
            if allow_again_inf[0]>0:
                oSYS_A_LOG.unlock_user(db_obj1, username)
                # reload LOGIN_DENY
                login_deny = db_obj1.col_val_where('DB_USER', {'DB_USER_ID': user_id}, 'LOGIN_DENY')
 
            else:
                raise BlinkError( 6, "Too many tries for this login.", 'login')         

        
        if login_method=='' or login_method==None:
            login_method='LOCAL'
        
        user_lib   = oDB_USER.mainobj(user_id)

        self._log('Login_Method:'+ login_method )
        debug.printx(__name__, "Login_Method: "+ login_method  )
        
        loginok = 0
        while(True):

            if login_method=='LDAP':
                
                self._log('Login_Method: '+ login_method )
                try:
                    
                    ldap_lib = LDAP_support()
                    ldap_lib.connect(username, password_in)
                    ldap_lib.authenticate()
                    
                except Blink_LDAP_Error:
                    self._log_fail(db_obj1, username, 2, 'LDAP: user/pw not valid.')
                    raise BlinkError( 2, "User or Password not valid.", 'login')  # password not valid
                except Exception:
                    raise BlinkError( 5, "LDAP server problem.", 'login')
                
                loginok = 1
                break
            
            if db_pw=='nopasswd':
                self._log('Login_Case: NOPASSWD')
                loginok = 2
                break            
                
            else:
                if user_lib.verify_pw( db_pw, password_in) < 1:
                    self._log_fail(db_obj1, username, 3, 'INTERN: PW not valid.')
                    raise BlinkError( 3, "User or Password not valid.", 'login')  # password not valid
                else:
                    loginok = 3
                    self._log('Login_Case: LOCAL_success')
            
            break # final break
        
        if login_deny>0:
            # NO _log_fail
            raise BlinkError( 6, "Account is locked.", 'login')         
        
        
        
        return { 'status':1, 'user_id': user_id, 'nick': username }
    
  
    def check_login(self, db_obj1, user_in, password_in):
        # standard login
        
        answer = self.check_verify(db_obj1, user_in, password_in)
        
        # update LOGIN_LAST
        user_args = {'LOGIN_LAST': db_obj1.Timestamp2Sql() }
        db_obj1.update_row('DB_USER', { 'DB_USER_ID': answer['user_id'] }, user_args)   
        
        return answer
        
     
    def _load_globals(self, db_obj):
        """
        load GLOBALS from DB
        """
        
        JSON_FORMAT= [
            'lib.paxml'
        ]
        
        sql_cmd = "NAME, VALUE from GLOBALS order by NAME"
        db_obj.select_tuple(sql_cmd)
        while db_obj.ReadRow():
            name = db_obj.RowData[0]
            val  = db_obj.RowData[1]
            if val!='':
                if name in JSON_FORMAT:
                    # data is saved as JSON-string
                    val = json.loads(val)
                self.session_obj['globals'][name]=val               
    
    def init_db_cache(self, db_obj):
        '''
        this method can be called without init of all other session vars ...
        '''
        
        self.session_obj['db_cache'] = {}
        initvars_lib = initvars_cls(self.session_obj)
        initvars_lib.init_all(db_obj)        
    
    def initvars(self, db_obj, user_in, password_in, dbid, user_id, access_config):
        
        self.session_obj['loggedin']=1
        '''
        * ALL session-vars: see docu "global variables"
        * sessvars: see docu "sessvars - Public Session variables"
        * :var sessvars: self.session_obj['sessvars']
       
            ['formback'][table] = {'id': ... }
            'objhist' : object history
        '''
        self.session_obj['sessvars'] = {}
        self.session_obj['sessvars']['debug.lev'] = 0
        
        
        self.session_obj['clip'] = {} # clipboard
        self.session_obj['table.select'] = {} # table select structure
        

        self.session_obj['sesssec']= {}   # secure session vars
        self.session_obj['sesssec']['user']     = user_in
        self.session_obj['sesssec']['password'] = password_in
        self.session_obj['sesssec']['dbid']     = dbid 
        self.session_obj['sesssec']['user_id'] = user_id


        '''
        access_config = {
            'dbname':'magasin',
            'host':'localhost',
            'user':'bl_42',
            'password':'xxxxxx',
          },
        '''
        self.session_obj['sesssec']['dbacc'] = access_config         
        self.session_obj['sesssec']['admin.flag'] = 0  # is admin ?
        '''
        more possible keys
       
        session['sesssec']['my.context'] : main GUI context of user: ACTIVE or EDIT
        session['sesssec']['my.role'] = 'ADMIN', 'EDITOR', 'VIEWER'
        '''
        
        # build DB cache
        self.init_db_cache(db_obj)
        
        # other vars
        user_lib = oDB_USER.mainobj(user_id)
        # self.session_obj['sesssec']['my.home.proj_id'] = user_lib.get_home_proj(db_obj)
        self.session_obj['sesssec']['admin.flag'] = user_lib.is_admin(db_obj)
        self.session_obj['sesssec']['user.sign'] = user_lib.get_sign(db_obj)
        
        roles = user_lib.get_roles(db_obj)
        self.session_obj['sesssec']['roles'] = roles        


        #self.session_obj['sesssec']['my.role'] = ''
        self.session_obj['sesssec']['my.context'] = 'EDIT' 
        self.session_obj['sesssec']['context.EDIT.admin.active'] = 0 # show ADMIN elements in the EDIT context ?
        
        self.session_obj['sesssec']['SW_Version'] = login.get_SW_version()

        self.session_obj['user_glob'] = {}   # user global vars
        # TBD: oUSER_PREF.MainLib.load(db_obj, self.session_obj['user_glob'] )  # load from database ...
        
        self.session_obj['globals']   =  config.superglobal

                
        # load globals from database
        # TBD: self._load_globals(db_obj)
        

   
               
  
        
class LDAP_support:
    '''
    LDAP support
    '''
    
    def __init__(self):
        self.conn = None
        
        if 'ldap' not in config.superglobal:
            raise BlinkError(1, 'No LDAP server configured. Please inform admin.')
        
        ldap_config = config.superglobal['ldap']
            
        self.ldap_server      = ldap_config['ldap_server'] # 'ldap://jenblidc01.blink.lan'
        self.user_domain_name = ldap_config['user_domain'] # 'blink.lan'
    
    def connect(self, user, password):

        s       = ldap3.Server( self.ldap_server, port=389, get_info = ldap3.ALL )
        user_dn = user + '@' + self.user_domain_name
        
        try:
            self.conn = ldap3.Connection(s, user= user_dn, password= password, check_names=True, lazy=False)
            self.conn.open()
        except:
            self.conn = None
            raise BlinkError(1, "Problem with LDAP-Server.") # user not exists


    def authenticate(self):
        
        answer = self.conn.bind()  
        
        if answer != True:
            raise Blink_LDAP_Error("LDAP Login faild.") # user not exists
        
        return answer
        
        
        