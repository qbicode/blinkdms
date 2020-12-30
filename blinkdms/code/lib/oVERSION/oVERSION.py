# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main DOC sub methods
File:           oVERSION.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from ..obj_mod import Obj_mod
from . import oVERSION_WFL
from . import oUPLOADS



class Mainobj:
    
    __id = None
    obj  = None # lib obj_abs()
    
    def __init__(self, idx):
        self.__id = idx
        self.obj = obj_abs('VERSION', idx)
        
    def features(self, db_obj):
        
        v_features = self.obj.main_feat_colvals(db_obj, {'*'})
        doc_id = v_features['DOC_ID']
        if not doc_id:
            raise BlinkError(1, 'Version has no DOC_ID.')
        
        self.docobj = obj_abs('DOC',  doc_id)
        d_features = self.docobj.main_feat_colvals(db_obj, {'*'})     
        
        sum_features = {**v_features, **d_features}
        return {'vals': sum_features}        

    def is_released(self, db_obj):
        '''
        this VERSION is RELEASED and ACTIVE? 
        '''
        
        v_features = self.features(db_obj)
        
        answer = 0
        if v_features['RELEASE_DATE'] is not None:
            if v_features['RELEASE_DATE'] != '':
                answer = 1
        
        if not v_features['IS_ACTIVE']:
            answer = 0
                
        debug.printx(__name__, '(55): VERSION_ID: '+str(self.__id)+'  RESULT:'+str(answer))
        
        return answer    

class Modify_obj(Obj_mod):
    """
    modify an object
    """
    
    def __init__(self, db_obj, objid=None):
        super().__init__(db_obj, 'VERSION', objid)

    def _next_version_no(self, db_obj, doc_id):
        
        sql_cmd = "count(VERSION) from VERSION where DOC_ID=" + str(doc_id)
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        version = db_obj.RowData[0]
        next_num = version + 1
        return next_num

    def new(self, db_obj, doc_id, args, options={}):
        ''' 
        create new version (NOT based on predecesor )
        TBD: check input
         AUTO create VERSION number + append DOC_ID
         args['vals']['DOC_TYPE_ID']
        '''
        
        if 'vals' not in args:
            raise BlinkError(1,'Input parameters missing.')

        next_num = self._next_version_no(db_obj, doc_id)

        args['vals']['DOC_ID'] = doc_id
        args['vals']['VERSION'] = next_num

        v_id = super().new(db_obj, args, options)

        # add log ...
        vers_wfl_lib = oVERSION_WFL.Modify_obj(db_obj, v_id)
        state_id = vers_wfl_lib.get_state_id_from_KEY('CREATED')
        audit_args = {
            'STATE_ID': state_id
        }
        vers_wfl_lib.simple_log_add(db_obj, audit_args)
        
        return v_id
        
    def new_successor(self, db_obj, old_vers_id):
        '''
        create successor
        '''
        
        objlib = obj_abs('VERSION', old_vers_id)
        old_features = objlib.main_feat_colvals(db_obj, '*')
        new_features = old_features.copy()

        new_features['RELEASE_DATE'] = None
        new_features['VALID_DATE'] = None
        new_features['IS_ACTIVE'] = 0
        new_features['EXPIRY_DATE'] = None
        args = {'vals': new_features}
        
        v_id = self.new(db_obj, old_features['DOC_ID'], args)

        #
        # copy uploads ....
        # get OLD data
        upload_lib = oUPLOADS.Mainobj(old_vers_id)
        upload_data_old = upload_lib.get_uploads_RAW(db_obj)

        # copy to NEW version
        upload_mod_lib = oUPLOADS.Modify_obj(db_obj, v_id)
        for upload_old_row in upload_data_old:
            upload_mod_lib.copy_one_upload(db_obj, upload_old_row)
        
        
        return v_id

    def update(self, db_obj, args, options={}):
        
        return super().update(db_obj, args, options)
        
        

    
class Table:
    """
    general static
    """

    @staticmethod
    def get_title_of_vers(db_obj, v_id):
        title = db_obj.col_val_where('VERSION', {'VERSION_ID': v_id}, 'NAME')
        return title
    
    
    def search_query_cond(self, text):

        full_query_cond = {
            'colcond': [
                {
                    'col': 'd.C_ID',
                    'op': 'LIKE',
                    'val': "%" + text + "%"
                }
               ],
            'join': 'DOC d on x.DOC_ID=d.DOC_ID',
            'where_after': 'group by x.DOC_ID'
        }

        return full_query_cond

    @staticmethod
    def count_match(db_obj, sqlfrom):

        sql_cmd = 'count(*) from ' + sqlfrom
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        cnt = db_obj.RowData[0]
        return cnt