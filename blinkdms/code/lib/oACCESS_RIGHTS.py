# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
basic management of CCT_ACCESS_RIGHTS
File:           oACCESS_RIGHTS.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>

:var acc_matrix_STRUCT:
   { 'read':0,1, 'write':0,1, ...}
   
:var  GRP_ACCESS_STRUCT: { DICT of struct
       grp_id : { read:0,1, insert:0,1 , write:0,1 delete:0,1 entail:0,1 }
    }
:var  GRP_ACCESS_X_STRUCT: [ LIST of struct
       'grp': grp_id, 'grp.nice':'nice name' 'mx': { read:0,1, insert:0,1 , write:0,1 delete:0,1 entail:0,1 }
    ]
"""
from blinkdms.code.lib.imports_min import *


#all object access rights
obj_acc_rights      = ['read', 'write', 'insert', 'delete', 'entail']
obj_acc_sql_rights  = ['select_right',  'update_right', 'insert_right', 'delete_right', 'entail_right']


class Obj_one:
    '''
    FUTURE: set CCT_ACCESS_RIGHTS for one object
    '''

    def __init__(self, acc_id):
        self.acc_id = acc_id
        
    def set_bo_id(self, db_obj, table, obj_id):
        '''
        set acc_id by giving Business object
        '''
        pk = table+'_ID'
        self.acc_id = db_obj.col_val(table, pk, obj_id, 'CCT_ACCESS_ID')
        
    def access_check(self, db_obj):
        '''
        get summary rights for the current user
        :return acc_matrix_STRUCT:
        '''
        return Methods.access_check(db_obj, '', None, self.acc_id)
        
    def get_obj_rights(self, db_obj):
        '''
        get GRP_ACCESS_X_STRUCT of access entry
        '''
       
        tmp_col_arr = ['USER_GROUP_ID'] + obj_acc_sql_rights  
        col_str = ', '.join(tmp_col_arr)
        
        sql_cmd = col_str + " from CCT_ACCESS_RIGHTS where CCT_ACCESS_ID=" + str(self.acc_id)
        db_obj.select_tuple(sql_cmd)
            
        all_data = []
        while db_obj.ReadRow():
            grpid = db_obj.RowData[0] 
            data_row = {}
            
            i=1 # starts from1, because index=0 for USER_GROUP_ID
            for nice_col in obj_acc_rights:
                data_row[nice_col] = db_obj.RowData[i]
                i=i+1
            
            all_data.append( {'grp':grpid, 'mx':data_row } )
            
        return all_data
    
    def remove_all(self, db_obj):
        '''
        REMOVE all access entryies
        '''   
        if not self.acc_id:
            raise BlinkError(1,'No access_id set.') 
        
        pk_dict = {'CCT_ACCESS_ID': self.acc_id}
        db_obj.del_row('CCT_ACCESS_RIGHTS', pk_dict)        
    
    def acc_all_set(self, db_obj, acc_many_matrix):
        '''
        SET all access entries, old entries will be removed
        :param acc_many_matrix: GRP_ACCESS_STRUCT
        ''' 
        if not self.acc_id:
            raise BlinkError(1,'No access_id set.')
        
        self.remove_all(db_obj)
        self.acc_many_add(db_obj, acc_many_matrix)
    
    def acc_add(self, db_obj, grp_id, acc_matrix):
        '''
        add access for ONE group
        :param acc_matrix: acc_matrix_STRUCT
        ''' 
        # check group in rights exists
        exists_id = db_obj.col_val_where('CCT_ACCESS_RIGHTS', {'CCT_ACCESS_ID': self.acc_id,'USER_GROUP_ID': grp_id}, 'CCT_ACCESS_ID')
        if exists_id:
            raise BlinkError(1,'Access right entry ('+str(self.acc_id)+',' + str(grp_id) + ') already exists')

        defRights = obj_acc_rights
        
        argu = { 
            'CCT_ACCESS_ID': self.acc_id,
            'USER_GROUP_ID': grp_id
        }
        i=0
        val_sum = 0
        for key in defRights: # for all defined features ...
            val = acc_matrix.get(key, 0)
            key_sql = obj_acc_sql_rights[i]
            val_sum = val_sum + val
            argu[key_sql] = val
            i=i+1

        if not val_sum:
            # access matrix is empty: do NOT save it ...
            return

        db_obj.insert_row('CCT_ACCESS_RIGHTS' , argu )
        
    def acc_many_add(self, db_obj, acc_many_matrix):
        '''
        add many access entryies
        :param acc_many_matrix: GRP_ACCESS_STRUCT
        '''
        for grp_id, acc_matrix in acc_many_matrix.items():
            self.acc_add(db_obj, grp_id, acc_matrix)
       
class Methods:
    '''
    statuc methods
    '''
    
    @staticmethod
    def get_obj_acc_rights():
        return obj_acc_rights
    
    @staticmethod
    def get_obj_acc_rights_ENA():
        '''
        get all object rights ENABLED
        '''
        acc_rigth_dict = {}
        for rig in obj_acc_rights:
            acc_rigth_dict[rig] = 1
        return acc_rigth_dict
    
    @staticmethod
    def get_obj_acc_rights_DIS():
        '''
        get all object rights DISABLED
        '''
        acc_rigth_dict = {}
        for rig in obj_acc_rights:
            acc_rigth_dict[rig] = 0
        return acc_rigth_dict    
    
    @staticmethod
    def access_check(db_obj, tablename, objid):
        '''
        * get the SUMMARY rights for one user of one object
            - by default the READ-flag == 1
            - when _SESSION['globals']["security_level"] == "select_on" : analyse the READ-flag
         :param object: db_obj
         :param string tablename:
         :param long objid : can be None
         FUTURE: 
         :param long cct_access_id-. # optional, if you know it, you can save some db-calls
         :param dict opt: "useReadFlag" 0,1 -- get the real READ-flag from cct_access_rights,
                even if _SESSION['globals']["security_level"] != "select_on"
        :return acc_matrix_STRUCT:
        '''

        if GlobMethods.is_admin():
            return Methods.get_obj_acc_rights_ENA()

        # 
        # FUTURE ..
        # tmp_useReadFlag = 0
        # if  (session['globals']["security_level"] == "select_on") OR (opt["useReadFlag"]>0):
        #       tmp_useReadFlag = 1
        
       
        o_rights = { "read":1, "write":0, "delete":0, "insert":0, "entail":0 }
        
        return o_rights
    
    @staticmethod
    def get_user_mygrp (db_obj, user_id):
        '''
        * get 'single user group' of user user_id
        * -use session['sessvars'][o.DB_USER."+str(user_id)+".mygroup] as cache 
        * :param object sql
        * :param int user_id
        * @return group_id
        '''
    
    
        group_id = 0
        user_key = "o.DB_USER."+str(user_id)+".mygroup"
        if user_key not in session['sessvars']: # TBD: o.DB_USER.mygroup is cached ???
            
            sql_cmd_0="SELECT USER_GROUP_ID FROM USER_GROUP WHERE db_user_id="+str(user_id)+" AND SINGLE_USER=1"
            sql_cmd  ="USER_GROUP_ID from DB_USER_IN_GROUP where DB_USER_ID="+str(user_id)+" and USER_GROUP_ID in ("+sql_cmd_0+")"
            db_obj.select_tuple(sql_cmd)
            if db_obj.ReadRow():
                group_id = db_obj.RowData[0]
                session['sessvars'][user_key] = group_id
            else:
                session['sessvars'][user_key] = group_id  # no entry in database, set cache to NOT_EXIST
        else:
            group_id = session['sessvars'][user_key]
           
        return (group_id)

    
    
