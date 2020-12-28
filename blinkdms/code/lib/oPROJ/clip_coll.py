# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
handle the clipboard collection
File:           clip_coll.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.main_imports import *
from .oPROJ     import mainobj, modify_obj
from .oPROJ_sub import oPROJ_assoc_mod

class clip_coll:
    
    def __init__(self, db_obj):
        # TBD find other architectural solution
        # create/get the personal clipboard base project
        
        self._has_clip_proj = 0
        self.clip_proj = 0


    
    def has_clip_proj(self):
        return self._has_clip_proj
        
    def get_proj_id(self):
        return self.clip_proj
    
    
    def add_objects(self, db_obj, table, objids):
        
        proj_mod_lib = oPROJ_assoc_mod(db_obj, self.clip_proj)
        for objid in objids:
            proj_mod_lib.add_obj(db_obj, table, objid)
            
    def add_objects_sql(self, db_obj, db_obj2, table, sql_from_order):
        
        proj_mod_lib = oPROJ_assoc_mod(db_obj, self.clip_proj)
        
        tablib = table_cls(table)
        pk_col = tablib.pk_col_get()
        sql_cmd = "x."+ pk_col +" from " + sql_from_order
        db_obj2.select_tuple(sql_cmd)  
        
        cnt=0
        while db_obj2.ReadRow():
    
            objid  = db_obj2.RowData[0]
            answer = proj_mod_lib.add_obj(db_obj, table, objid)
            cnt = cnt + 1
            
        return cnt
    
    def get_obj_num(self, db_obj, table):
        """
        get number of elements
        """
        proj_lib = mainobj(self.clip_proj)
        cnt = proj_lib.cnt_elems_of_table(db_obj, table)
        return cnt