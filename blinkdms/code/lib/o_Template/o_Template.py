# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
TEMPLATE: get info of related objects
File:           oTEMPLATE/xxx.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from ..obj_mod import Obj_mod

class Mainobj:
    """
    sinngle object class
    """
    __id = None
    obj  = None # lib obj_abs()
    
    def __init__(self, id):
        self.__id = id
        self.obj = obj_abs('XXX', id)


class Table:
    """
    general table methods, static ?
    """
    def __init__(self):
        pass
    
class Modify_obj(obj_mod):
    """
    modify an object
    """
    
    def __init__(self, db_obj, objid=None):
        super().__init__(db_obj, 'XXXXX', objid) # TBD: insert table name here