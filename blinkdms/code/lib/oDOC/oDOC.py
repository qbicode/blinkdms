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

class Modify_obj(Obj_mod):
    """
    modify an object
    """
    
    def __init__(self, db_obj, objid=None):
        super().__init__(db_obj, 'DOC', objid)

  
        
        

    
