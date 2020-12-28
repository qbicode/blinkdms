# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main DB_USER sub methods
File:           oDB_USER.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
import hashlib
import random
from flask import session

from ..obj_sub import table_cls, obj_abs
from ..debug import debug
from ..f_utilities import BlinkError
from ..obj_mod import Obj_mod
from .. import oROLE
from blinkdms.code.lib.oSTATE import oSTATE


class mainobj:
    
    __id = None
    obj  = None # lib obj_abs()
    
    def __init__(self, idx):
        self.__id = idx
        self.obj = obj_abs('DB_USER', idx)

    def is_admin(self, db_obj):
        """
        user is admin ? analyse "root" or SU-flag
        :return int: 0,1
        """
        col_arr = ['SU', 'NICK']
        user_tab_obj = table_cls('DB_USER')
        val_dict = user_tab_obj.element_get(db_obj, {'DB_USER_ID':self.__id}, col_arr)  # self.obj.main_feat_colvals(db_obj, col_arr)
        
        answer = 0
        if val_dict['NICK']=='root':
            answer=1        
        
        if val_dict['SU']>0:
            answer=1
        return answer

    def get_sign(self, db_obj):
        '''
        get short signature of user, two letters
        '''
        col_arr= ('FULL_NAME',)
        full_name = self.obj.main_feat_val(db_obj, 'FULL_NAME')
        if full_name == None:
            return '??'
        
        words = full_name.split(' ')
        sign = words[0][0]
        if len(words) > 1:
            sign = sign + words[1][0]

        sign = sign.upper()
        return sign
    
    def features(self, db_obj):
        # all features
        return self.obj.main_feat_colvals(db_obj, ['*'])
        
    def get_fullname(self, db_obj):
        """
        get full name of user
        """
        col_arr = ('FULL_NAME',)
        val_arr = self.obj.main_feat_colvals(db_obj, col_arr)
        
        if val_arr['FULL_NAME'] is None:
            val_arr['FULL_NAME']=''
        
        return val_arr['FULL_NAME']
    
    def get_home_proj(self, db_obj):
        
        col_arr= ('PROJ_ID',)
        val_arr = self.obj.main_feat_colvals(db_obj, col_arr)  
        return val_arr['PROJ_ID']
    
  
    
    def get_groups(self, db_obj):
        """
        get groups of user
        """
        groups=[]
        sql_cmd = 'x.user_group_id from DB_USER_IN_GROUP x  where x.db_user_id=' + str(self.__id) + ' order by x.user_group_id'
        db_obj.select_tuple(sql_cmd)
        while db_obj.ReadRow():
            group_id = db_obj.RowData[0]  
            groups.append(group_id)
        return groups
    
    def get_roles(self, db_obj):
        """
        get roles of user
        :return [role-keys]
        """
        
        role_arr = []
        
        role_str = self.obj.main_feat_val(db_obj, 'ROLES')
        
        if role_str == '' or role_str == None:
            return []

        role_arr = role_str.split(',')
        
        return role_arr
    
    def get_login_method(self, db_obj):
        '''
        :return: string LOCAL or LDAP
        '''
        col_arr = ('LOGIN_METH',)
        val_arr = self.obj.main_feat_colvals(db_obj, col_arr)
        login_method = val_arr['LOGIN_METH']
        if login_method=='' or login_method==None:
            login_method='LOCAL'   
        return login_method
    
    def get_role_names(self, db_obj):
        """
        get roles of user
        :return: [[key, nicename]]
        """
        roles = self.get_roles(db_obj)
        role_names = []
        for role_key in roles:
            r_name = oROLE.Table.nicename_by_key(db_obj, role_key)
            role_names.append([role_key, r_name])
            
        return role_names    
    
    def has_role(self, db_obj, role_key):
        '''
        has role ROLE_KEY ?
        ROOT or user with SU=1 AUTOMATICALLY = 1
        :return: boolean
        '''
        
        if self.is_admin(db_obj):
            return 1
        
        has_role=0
        roles = self.get_roles(db_obj)
        if role_key in roles:
            has_role=1
            
        return has_role
    
    def role_rights_tab(self, db_obj, table):
        """
        get user role rights for a specific table
        """
        #TBD: rights = oROLE_basic.table_rights_user(db_obj, table)
        # return rights
        pass
    
    def has_func_right(self, db_obj, function_name ):
        """
        get user role right for specific function_name (e.g. 'ERP_import')
        :return: -1, 0, 1
        """
        right = 1 #FUTURE: right = oROLE_basic.right_allow_f(db_obj, function_name)
        
        return right
    
    def get_role_rights(self, db_obj ):
        """
        get all role rights
        :return: list of dict
        """
        if not self.__id:
            raise BlinkError(1, 'Class not initialized.')
        
        rights = [] #FUTURE: rights  = oROLE_basic.get_role_rights_user(db_obj, self.__id )
        return rights  

    def get_user_prefs(self, db_obj):
        '''
        get USER_PREF
        :return: {key:val}
        '''
              
        sql_cmd = "VAR_NAME, VALUE from USER_PREF where DB_USER_ID="+ (str(self.__id ))
        db_obj.select_tuple(sql_cmd)
        dataout = {}
        while db_obj.ReadRow():
            key = db_obj.RowData[0] 
            val = db_obj.RowData[1]
            dataout[key] = val
        return dataout

    def hash_pw_salt(self, password, salt_str):
        """
        create hash from salt+password
        """
        return Table.hash_pw_salt(password, salt_str)
        
        
    def hash_pw(self, password):
        """
        transform user_password into "salt:MD5"
        """
        return  Table.hash_pw(password) 
    
    def create_user_pw(self):
        """
        create strong password
        """     
        return Table.create_user_pw()
    
    def verify_pw(self, pw_db, password_in):
        """
        return 0 or 1
        """
        db_pw_arr = pw_db.split(':')
        salt_hex  = db_pw_arr[0].encode('ascii')
        
        pw_hash_user = self.hash_pw_salt(password_in, salt_hex)
        
        # debug.printx( __name__, 'PW_COMP:: pw_db:'+ str(pw_db) + ' IN:'+ password_in + ' HASGED:'+pw_hash_user)
        
        isok=0
        if pw_hash_user == pw_db:
            isok=1
            
        return isok
            
            
class modify_obj(Obj_mod):
    """
    modify an DB_USER
    """
    
    def __init__(self, db_obj, objid=None):
        super().__init__(db_obj, 'DB_USER', objid)
        
        
    def _check_user_nick(self, db_obj, NICK, ignore_self=0):
        
        # check for existing NICK
        sql_cmd = "DB_USER_ID, NICK from DB_USER where UPPER(NICK) like UPPER(" + db_obj.addQuotes(NICK) + ")"
        if ignore_self:
            sql_cmd = sql_cmd + " and DB_USER_ID!="+str(self.objid)
            
        db_obj.select_tuple(sql_cmd)
        if db_obj.ReadRow():
            user_id  = db_obj.RowData[0] 
            username = db_obj.RowData[1]    
            raise BlinkError(3,'User with login-name "' + NICK + '" already exists.') # do not show the DB NICK !        
        
        
    def update(self, db_obj, args, options={} ):
        
        #
        # do some checks
        #
        
        if 'vals' in args:
            if 'NICK' in args['vals']:  
                NICK = args['vals'].get('NICK','').strip()
                self._check_user_nick(db_obj, NICK, 1)
        
        super().update(db_obj, args, options)
        
    def new(self, db_obj, args, options={}):
        # check input 
        
        if 'vals' not in args:
            raise BlinkError(1,'Input parameters missing.')
        
        NICK = args['vals'].get('NICK').strip()
        if NICK=='':
            raise BlinkError(2,'Input parameters NICK missing.')
        
        args['vals']['NICK'] = args['vals']['NICK'].strip() # remove any trailing WHITESPACE ...
        if 'PASS_WORD' not in args['vals']:
            # set a password, but the user can not login with that one ...
            args['vals']['PASS_WORD'] = 'XXX'
            
        # check for existing NICK
        self._check_user_nick(db_obj, NICK)
        
        return super().new(db_obj, args, options)
    
    def ch_pwd(self, db_obj, password):
        '''
        change password
        time stamp for changing pw => see modification log
        '''
        user_lib = mainobj(self.objid)
        hash_pw = user_lib.hash_pw( password )
        
        params = { 
            'vals': {
                'PASS_WORD': hash_pw,
                }
            }
        self.update(db_obj, params)
        
    def set_login_denied(self, db_obj, flag):
        '''
        set LOGIN_DENY: WITHOUT table-cache !!!
        - because it is needed before a login ...
        '''
        params = {
            'LOGIN_DENY': flag
        }
        db_obj.update_row('DB_USER', { 'DB_USER_ID': self.objid }, params)
        
    def add_role(self, db_obj, role_id):
        '''
        :param role_id: string, gets sanitized
        add role to user
        '''
        user_id = self.objid
        role_id = role_id.strip()
        
        user_lib = mainobj(user_id)
        old_roles = user_lib.get_roles(db_obj)

        if role_id in old_roles:
            # already exists
            return
        
        old_roles.append(role_id)
        role_str = ','.join(old_roles)
        args = {
            'vals': {
                'ROLES': role_str
            }
        }
        super().update(db_obj, args)
        
    def del_role(self, db_obj, role_id):
        '''
        delete role from user
        '''
        user_id = self.objid
        user_lib = mainobj(user_id)
        old_roles = user_lib.get_roles(db_obj)
        old_roles.remove(role_id)  # remove element
        role_str = ','.join(old_roles)
        args = {
            'vals': {
                'ROLES': role_str
            }
        }
        super().update(db_obj, args)
           
    
    def add_group(self, db_obj, group_id):
        '''
        add group to user
        '''
        user_id = self.objid
        sql_cmd = 'DB_USER_ID from DB_USER_IN_GROUP where DB_USER_ID=' + str(user_id) + ' and USER_GROUP_ID='+str(group_id)
        db_obj.select_tuple(sql_cmd)
        if db_obj.ReadRow():
            # already exists
            return        
        
        role_mod_obj = Obj_mod(db_obj, 'DB_USER_IN_GROUP')
        args={ 
            'USER_GROUP_ID': group_id,
            'DB_USER_ID'   : user_id
       
        }
        role_mod_obj.new_simple(db_obj, args)  
        
    def crea_my_grp(self, db_obj):
        '''
        create personal group
        '''
        
        user_id = self.objid
        nick    = db_obj.col_val('DB_USER', 'DB_USER_ID', user_id, 'NICK')
        
        old_grp_id    = db_obj.col_val_where('USER_GROUP', {'NAME': nick, 'SINGLE_USER':1 }, 'USER_GROUP_ID')
        if old_grp_id:
            return
        
        # create group
        grp_args= {
          'vals': {
              'NAME': nick,
              'SINGLE_USER': 1,
              'DB_USER_ID': user_id # admin ...
          }
        }
        grp_mod_obj = Obj_mod(db_obj, 'USER_GROUP')
        new_grp_id  = grp_mod_obj.new(db_obj, grp_args)
        
        self.add_group(db_obj, new_grp_id)  
        
    def get_Template_user(self, db_obj):
        user_id    = db_obj.col_val_where('DB_USER', {'NICK': 'TEMPLATE' }, 'DB_USER_ID')
        return user_id
    
    def save_user_pref(self, db_obj, key, val):
        user_id = self.objid
        pk_dict = {
            'DB_USER_ID': user_id,
            'VAR_NAME':   key
        }
        args =  {
            'VALUE':val
        }
        db_obj.insert_update('USER_PREF', pk_dict, args)                    
    
class Table:
    """
    general static
    """
    
    @staticmethod
    def getUserByEmail(db_obj, email):
        '''
        get first USER_ID by email-address field
        '''
        user_id = 0
        sql_cmd = "DB_USER_ID from DB_USER where UPPER(EMAIL) like UPPER(" + db_obj.addQuotes(email) + ")"
        db_obj.select_tuple(sql_cmd)
        if db_obj.ReadRow():
            user_id  = db_obj.RowData[0] 
        return user_id  
    
    @staticmethod
    def get_user_by_nick(db_obj, username):
        '''
        get user_id by NICK
        :return: int 0 or ID
        '''
        user_id=0
        sql_cmd = "DB_USER_ID from DB_USER where UPPER(NICK) like UPPER(" + db_obj.addQuotes(username) + ")"
        db_obj.select_tuple(sql_cmd)
        if db_obj.ReadRow():
            user_id  = db_obj.RowData[0]  
        return user_id
    
    @staticmethod
    def get_fullname(db_obj, user_id):  
        return db_obj.col_val('DB_USER', 'DB_USER_ID', user_id, 'FULL_NAME' )  
    
    @staticmethod
    def hash_pw(password):
        """
        transform user_password into "salt:MD5"
        """
        
        salt = os.urandom(16)
        salt_str = salt.hex().encode('ascii')
        
        output = Table.hash_pw_salt(password, salt_str)
        return output
    
    @staticmethod
    def hash_pw_salt(password, salt_str):
        """
        create hash from salt+password
        """
        m = hashlib.md5()
        m.update(salt_str + password.encode('ascii') )
        pw_hash = m.hexdigest()
        output  = salt_str.decode('ascii')+':'+ pw_hash

        return output    
    
    @staticmethod
    def create_user_pw():
        """
        create strong password
        """     

        chars = "abcdefghijklmnopqrstuvwxyziABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890^?!?$%&/()=?+#*~;:_,.-<>|"
        password = ""
        length   = 12
        while len(password) != length:
            password = password + random.choice(chars)
            if len(password) == length:
                break 
        return password
    
    @staticmethod
    def sql_user_has_role(db_obj, role_key):
        sql_from ='ROLES like '+db_obj.addQuotes('%'+role_key+'%')
        return sql_from

    @staticmethod
    def get_users_review(db_obj, state_key: str):
        '''
        get ALL possible review users for REVIEW or RELEASE
        - select by user.role
        - only active users
        '''
        
        if state_key==oSTATE.REVIEW:
            # select by role
            sql_where_add = Table.sql_user_has_role(db_obj, 'edit')
            
        if state_key==oSTATE.RELEASE:
            # select by role
            # FUTURE: only allowed to riole "qm"
            sql_where_add = Table.sql_user_has_role(db_obj, 'edit')        
        
        sql_where_add = sql_where_add + " and IS_ACTIVE=1"    

        data = []
        sql_cmd = "DB_USER_ID, FULL_NAME from DB_USER where "+sql_where_add+" order by FULL_NAME"
        db_obj.select_tuple(sql_cmd)
        while db_obj.ReadRow():
            data.append([db_obj.RowData[0], db_obj.RowData[1]])
        return data