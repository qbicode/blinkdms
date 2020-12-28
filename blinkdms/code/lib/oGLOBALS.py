# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"
"""
standard methods for globals
File:           oGLOBALS.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.db import db

class Methods:
    
    @staticmethod
    def get_val(db_obj , key):
        result = db_obj.col_val('globals', 'name', key, 'value')
        return result
    
    @staticmethod
    def save_val( db_obj, key, val, notes ):
        pk_dict= {'NAME':key}
        args={
          'VALUE':val,
          'NOTES':notes
        }
        db_obj.insert_update('GLOBALS', pk_dict, args)