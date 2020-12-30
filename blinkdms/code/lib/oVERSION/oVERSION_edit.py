# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main VERSION : EDIT special activities
File:           oVERSION_edit.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from ..obj_mod import Obj_mod, Obj_assoc_mod
from blinkdms.code.lib.oDOC import oDOC_VERS
from blinkdms.code.lib.oSTATE import oSTATE


class Mainobj:
    
    __id = None
    obj = None  # lib obj_abs()
    v_features = None  # all VERSION features
    d_features = None  # all DOC features
    doc_id = None
    
    def __init__(self, db_obj, idx):
        self.__id = idx
        self.obj = obj_abs('VERSION', idx)
        
        doc_lib = oDOC_VERS.Table('EDIT')
        self.view_table = doc_lib.table

        self.v_features = self.obj.main_feat_colvals(db_obj, {'*'})

        self.doc_id = self.v_features['DOC_ID']
        if not self.doc_id:
            raise BlinkError(1, 'Version has no DOC_ID.')
        
        self.docobj = obj_abs('DOC',  self.doc_id)
        self.d_features = self.docobj.main_feat_colvals(db_obj, {'*'})
        
    def get_docs_id(self):
        return self.doc_id

    def features(self, db_obj):
        '''
        feature sof DOC and VERSION
        '''
        sum_features = {**self.d_features, **self.v_features} # warning D-notes will be overwritten
        sum_features['d.NOTES'] = self.d_features['NOTES'] # repaier overwriting of NOTES
        return {'vals': sum_features}

    def get_current_versid(self, db_obj):
        # return VERSION_ID
        
        sql_cmd = 'VERSION_ID from ' + self.view_table + ' where DOC_ID=' + str(self.v_features['DOC_ID'])
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        got_id = db_obj.RowData[0]
        return got_id
    
    def is_current_versid(self, db_obj):
        # return 0 or 1
        
        flag=0
        curr_id = self.get_current_versid(db_obj)
        if curr_id==self.__id:
            flag=1
            
        return flag    

    def edit_allowed(self, db_obj):
        return 1

    def workflow_is_active(self, db_obj):
        answer = 0
        if self.v_features['WFL_ACTIVE'] is not None:
            if self.v_features['WFL_ACTIVE'] > 0:
                answer = self.v_features['WFL_ACTIVE']
        return answer

    def is_owner(self, db_obj):
        '''
        user is owner of this version? 
        '''
        is_owner_flag = 0
        doc_user_id = self.d_features.get('DB_USER_ID')
        if session['sesssec']['user_id'] == doc_user_id:
            is_owner_flag = 1
        
        return is_owner_flag    
    
    def is_released(self, db_obj):
        '''
        this VERSION is RELEASED and ACTIVE? 
        FUTURE: use static method from oVERSION.py
        '''
        
        answer = 0
        if self.v_features['RELEASE_DATE'] is not None:
            if self.v_features['RELEASE_DATE'] != '':
                answer = 1
        
        if not self.v_features['IS_ACTIVE']:
            answer = 0
                
        debug.printx(__name__, '(85): VERSION_ID: '+str(self.__id)+'  RESULT:'+str(answer))
        
        return answer
    
    
    def get_review_users_by_state(self, db_obj, state_id):
        '''
        get list of {POS,  DB_USER_ID, STATE_ID, DONE, PARALLEL }
        '''

        result = []
        doc_id = self.v_features['DOC_ID']
        sql_cmd = '* from AUD_PLAN where DOC_ID=' + str(doc_id) + ' and STATE_ID=' + str(state_id) + ' order by POS'
        db_obj.select_dict(sql_cmd)
        while db_obj.ReadRow():
            result.append( db_obj.RowData )
            
        return result      
    
    def get_review_users(self, db_obj):
        '''
        get ALL review users (ignore STATE_ID)  list of {POS,  DB_USER_ID, STATE_ID, DONE, PARALLEL }
        '''

        result = []
        doc_id = self.v_features['DOC_ID']
        sql_cmd = '* from AUD_PLAN where DOC_ID=' + str(doc_id) + ' order by POS'
        db_obj.select_dict(sql_cmd)
        while db_obj.ReadRow():
            result.append( db_obj.RowData )
            
        return result
    
     
        

class Modify_More():
    """
    modify an object
    """
    objid = 0
    
    def __init__(self, db_obj, objid):

        self.objid = objid
        info_lib = Mainobj(db_obj, objid)
        self.doc_id = info_lib.doc_id
        
    def reviewers_clean_all(self, db_obj):
        # delete all reviewers + Editors
        db_obj.del_row('AUD_PLAN', {'DOC_ID': self.doc_id} )        

    def update_reviewers(self, db_obj, reviewers, state_id):

        # delete all with state
        db_obj.del_row('AUD_PLAN', {'DOC_ID': self.doc_id, 'STATE_ID':state_id} )
        
        debug.printx(__name__, '(106) state_id: '+str(state_id)+' reviewers:' + str(reviewers), 1)

        assoc_lib = Obj_assoc_mod(db_obj, 'AUD_PLAN', self.doc_id)
        for user_id in reviewers:

            pos = assoc_lib.get_new_pos(db_obj, 'POS')
            args = {
                'POS': pos,
                'DB_USER_ID': user_id,
                'STATE_ID': state_id
            }
            assoc_lib.new(db_obj, args)
            

class VersionsOfUser:

    def __init__(self, user_id):
        self.user_id = user_id
        doc_lib = oDOC_VERS.Table('EDIT')
        self.view_table = doc_lib.table        

    def get_sql_from_open_versions(self, db_obj):
        '''
        get SQL: 'table where x=y'
        '''
        sql_cmd = self.view_table + ' x ' + \
           ' where x.DOC_ID in (select DOC_ID from AUD_PLAN where DB_USER_ID=' + str(self.user_id) + ' and DONE=1)'
        return sql_cmd
        
        
    
            
