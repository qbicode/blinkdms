# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
TEMPLATE: get info of related objects
File:           oTEMPLATE/xxx.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *

# KEY => nice name
ROLE_DEFS = {
   'edit': 'Editor',
   'folder.ed': 'Folder.Edit',
   'admin': 'Admin',
   'view': 'Viewer',
   'qm': 'QM'
}

# translator, if an internal KEY changes
ROLE_KEY_EDIT ='edit'
ROLE_KEY_VIEW ='view'
ROLE_KEY_FOLDER_EDIT='folder.ed'
ROLE_KEY_ADMIN='admin' 



class Table:
    """
    general table methods, static ?
    """
    def __init__(self):
        pass

    @staticmethod
    def get_all_roles(db_obj):
        '''
        get roles (KEY, Nice name)
        '''
        return ROLE_DEFS
    
    @staticmethod
    def get_all_roles_nice(db_obj):
        '''
        get roles (KEY, Nice name)
        '''

        result = []
        for key, val in ROLE_DEFS.items():
            result.append({'KEY': key, 'NAME': val})
        return result

    @staticmethod
    def nicename_by_key(db_obj, key):
        '''
        get roles (KEY, Nice name)
        '''
        nice = ROLE_DEFS[key]
        return nice 
