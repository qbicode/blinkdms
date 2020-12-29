# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main DOC sub methods
File:           oDOC.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from ..obj_mod import Obj_mod



class Mainobj:
    
    __id = None
    obj  = None # lib obj_abs()
    
    def __init__(self, idx):
        self.__id = idx
        self.obj = obj_abs('DOC', idx)
        
    def all_versions(self, db_obj):
        '''
        get ALL versions of DOC
        :return: [] of VERSION_ID
        '''
        version_ids = []
        sql_cmd = 'VERSION_ID from VERSION where DOC_ID=' + str(self.__id) + ' order by VERSION'
        db_obj.select_tuple(sql_cmd)
        while db_obj.ReadRow():
            v_id = db_obj.RowData[0]
            version_ids.append(v_id)
        return version_ids

class Modify_obj(Obj_mod):
    """
    modify an object
    """
    
    def __init__(self, db_obj, objid=None):
        super().__init__(db_obj, 'DOC', objid)

  
        
        

    
