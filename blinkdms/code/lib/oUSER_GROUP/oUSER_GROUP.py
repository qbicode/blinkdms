# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
oUSER_GROUP
File:           oUSER_GROUP/oUSER_GROUP.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *

class Mainobj:
    
    __id = None
    obj  = None # lib obj_abs()

    
    def __init__(self, grp_id):
        '''
        :param context: 
           'SERVICE' - service
           'EU'      - end user
        '''
        self.__id = grp_id

        

    def get_users(self, db_obj):
        """
        get IDs of users
        """

        table_lib = table_cls('DB_USER')
        
        user_arr = []
        sqlstate = 'DB_USER_ID from DB_USER_IN_GROUP where USER_GROUP_ID='+str(self.__id)
        db_obj.select_tuple( sqlstate )
        while db_obj.ReadRow():
            user_id = db_obj.RowData[0]    
            user_arr.append(user_id)
        return user_arr    


class Table:
    """
    general table methods, static ?
    """
    def __init__(self):
        pass
 
    @staticmethod
    def non_single_groups_active(db_obj):
        '''
        get all active NON-SINGLE groups
        '''
        sqlstate = 'USER_GROUP_ID, NAME from USER_GROUP where SINGLE_USER=0 or SINGLE_USER is NULL order by NAME'
        db_obj.select_tuple( sqlstate )
        outlist=[]
        while db_obj.ReadRow():
            outlist.append( [db_obj.RowData[0],  db_obj.RowData[1]] ) 
            
        return outlist
        