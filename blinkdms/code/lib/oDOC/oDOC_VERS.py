# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main DOC sub methods
File:           oDOC.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *


class Table:
    """
    general static
    """
    
    table = ''

    def __init__(self, context):
        '''
        :param context: EDIT, ACTIVE
        '''
        self.context = context
        if self.context != 'EDIT' and self.context != 'ACTIVE':
            raise BlinkError(1, 'Bad context.')

        self.context_info = {
            'EDIT': {'table': 'DOC_VERS_EDIT'},
            'ACTIVE': {'table': 'DOC_VERS_ACTIVE'},
        }
        self.table = self.context_info[context]['table']
        
    def get_version_id(self, db_obj, doc_id):
        v_id = 0
        sql_cmd = 'VERSION_ID from ' + self.table + ' where DOC_ID=' + str(doc_id)
        db_obj.select_tuple(sql_cmd)
        if db_obj.ReadRow():
            v_id = db_obj.RowData[0]
        return v_id

    def get_features_by_doc_id(self, db_obj, doc_id):
        '''
        get all features of one VERSION by DOC_ID
        '''

        sql_cmd = '* from ' + self.table + ' where DOC_ID=' + str(doc_id)
        db_obj.select_dict(sql_cmd)
        features = {}
        if db_obj.ReadRow():
            features = db_obj.RowData
        return features
    

    def get_version_by_cid(self, db_obj, cid):
        v_id = 0
        sql_cmd = 'VERSION_ID from ' + self.table + ' where C_ID=' + db_obj.addQuotes(cid)
        db_obj.select_tuple(sql_cmd)
        if db_obj.ReadRow():
            v_id = db_obj.RowData[0]
        return v_id    
    
    def search_cond_EDIT(self, text):
        '''
        get query for EDIT database
        '''
        full_query_cond = {
            'table' : 'DOC_VERS_EDIT',
            'colcond': [
                {
                    'col': 'x.C_ID',
                    'op': 'LIKE',
                    'val': "%" + text + "%"
                },
                {
                    'col'  : 'x.NAME',
                    'op'   : 'LIKE',
                    'val'  : "%" + text + "%",
                    'logop': 'OR'
                },                
               ],
        }

        return full_query_cond

    def search_EDIT_owner(self, user_id):
        '''
        get query for EDIT database
        '''
        full_query_cond = {
            'table': 'DOC_VERS_EDIT',
            'colcond': [
                {
                    'col': 'x.DB_USER_ID',
                    'op': '=',
                    'val': user_id
                },

               ],
        }

        return full_query_cond    

    def search_cond_ACTIVE(self, text):
        '''
        get query for ACTIVE database
        '''
        full_query_cond = {
            'table': 'DOC_VERS_ACTIVE',
            'colcond': [
                {
                    'col': 'x.C_ID',
                    'op': 'LIKE',
                    'val': "%" + text + "%"
                },

               ],
        }

        return full_query_cond    

    @staticmethod
    def count_match(db_obj, sqlfrom):

        sql_cmd = 'count(*) from ' + sqlfrom
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        cnt = db_obj.RowData[0]
        return cnt

    