
"""
main WFL methods - workflow type
File:           oWFL.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *

KEY_REL_ONLY    ='REL_ONLY'
KEY_REV_REL     ='REV_REL'
KEY_NO_WORKFLOW ='NO_WFL'

class Mainobj:
    """
    sinngle object class
    """
    __id = None
    obj  = None # lib obj_abs()
    
    def __init__(self, id):
        self.__id = id
        self.obj = obj_abs('WFL', id)

    def get_type(self, db_obj):
        # get main type keys 
        typex = self.obj.main_feat_val(db_obj, 'KEYX')
        return typex