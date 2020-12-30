# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main VERSION : ACTIVE special activities
File:           oVERSION_active.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.oDOC import oDOC_VERS


class Mainobj:
    
    __id = None
    obj = None  # lib obj_abs()
    v_features = None  # all VERSION features
    d_features = None  # all DOC features
    doc_id = None
    
    def __init__(self, idx):
        self.__id = idx
        self.obj = obj_abs('VERSION', idx)
        
        doc_lib = oDOC_VERS.Table('ACTIVE')
        self.view_table = doc_lib.table
        
    def version_exists(self, db_obj):
        answer = 0
        
        table_lib = table_cls(self.view_table)
        if table_lib.element_exists(db_obj, {'VERSION_ID':self.__id}):
            answer = 1
        return answer