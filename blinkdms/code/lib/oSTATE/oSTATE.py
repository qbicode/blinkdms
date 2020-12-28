# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
STATE things
File:           oSTATE.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.f_utilities import BlinkError

# major keys
REVIEW ='REVIEW'
RELEASE='REVIEW_REL'

class STATE_info:
    '''
    keys:
       'CREATED'
       'REJECT'
       'REL_START'
       'REL_END' : final release state
       'WF_END' : workflow end (e.g. rejected)
       'REVIEW' : reviewed
       'REVIEW_REL' : release reviewed
    '''
    all_entries_by_key = None
    all_entries_by_id = None

    
    @staticmethod
    def get_stateid_by_key(db_obj, key):

        if STATE_info.all_entries_by_key is None:
            STATE_info.all_entries_by_key = STATE_info.get_all_by_key(db_obj)

        if key not in STATE_info.all_entries_by_key:
            return 0

        state_id = STATE_info.all_entries_by_key[key]['STATE_ID']
        return state_id
    
    @staticmethod
    def get_statekey_by_id(db_obj, state_id):

        if STATE_info.all_entries_by_id is None:
            STATE_info.all_entries_by_id = STATE_info.get_all_by_id(db_obj)

        if state_id not in STATE_info.all_entries_by_id:
            raise BlinkError(1, 'State-id '+str(state_id)+ ' not found.')

        key = STATE_info.all_entries_by_id[state_id]['NAME']
        return key
    
    @staticmethod
    def get_nice_by_id(db_obj, state_id):

        if STATE_info.all_entries_by_id is None:
            STATE_info.all_entries_by_id = STATE_info.get_all_by_id(db_obj)

        if state_id not in STATE_info.all_entries_by_id:
            raise BlinkError(1, 'State-id '+str(state_id)+ 'not found.')

        key = STATE_info.all_entries_by_id[state_id]['NICE']
        return key    

    @staticmethod
    def get_all(db_obj):
        
        sql_cmd = "* from STATE order by STATE_ID"
        db_obj.select_dict(sql_cmd)

        all_data = []
        while db_obj.ReadRow():
            all_data.append(db_obj.RowData)

        return all_data
    
    @staticmethod        
    def get_all_by_key(db_obj):
        result = {}
        data = STATE_info.get_all(db_obj)
        for row in data:
            result[row['NAME']] = row

        return result
    
    @staticmethod
    def get_all_by_id(db_obj):
        result = {}
        data = STATE_info.get_all(db_obj)
        for row in data:
            result[row['STATE_ID']] = row

        return result

    