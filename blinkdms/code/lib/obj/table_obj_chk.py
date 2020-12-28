# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
do access check for TABLE and/or OBJECT
File:           table_obj_chk.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.main_imports import *
#from blinkapp.code.lib import oROLE_basic
#from blinkapp.code.lib import oACCESS_RIGHTS

ADMIN_OK_TABLES = [
    {'t': 'DB_USER', 'rights':    {'read': 1, 'write': 1, 'insert': 1}},
    {'t': 'DOC',     'rights':    {'read': 1, 'write': 0, 'insert': 0}},
    {'t': 'USER_GROUP', 'rights': {'read': 1, 'write': 1, 'insert': 1}},
    {'t': 'DOC_TYPE', 'rights':   {'read': 1, 'write': 1, 'insert': 1}},
    {'t': 'DOC_VERS_ACTIVE', 'rights': {'read': 1, 'write': 0, 'insert': 0}},
    {'t': 'DOC_VERS_EDIT', 'rights':   {'read': 1, 'write': 0, 'insert': 0}},
    {'t': 'WFL', 'rights':   {'read': 1, 'write': 0, 'insert': 0}},

]

def right_of_admin_of_tab(db_obj, table):
    for row in ADMIN_OK_TABLES:
        if row['t'] == table:
            return row

def get_table_rights_user(db_obj, table):
    return {'write': 1, "insert": 1, "delete": 1}

def get_object_rights_user(db_obj, table, obj_id):
    return {'write': 1, "insert": 1, "delete": 1}

def get_obj_acc_rights_DIS():
    return {'write': 0, "insert": 0, "delete": 0}

def get_TableMsg( tablename, rightx ):
    '''
    get nice error message on missing table right
    '''
    
    tab_lib = table_cls(tablename)
    nicename = tab_lib.nice_name()
    return 'You have no permission to "' + rightx + '" at table '+nicename+'. ' + \
            'Reason: You have no role right '  + rightx + ' for this object. '  + \
            'Please contact the administrator to get role rights.'   

def do_tab_obj_access_chk(db_obj, tablename, obj_id, act=None):
    """
     do access check for TABLE and/or OBJECT: standard: write-test
     :param obj_id: object ID; if None: No object test ...
     :param array act: 'tab' : [rights]
        'obj' : [ rights ]
        'tab'
         leave 'tab' or 'obj' as empty array, if you do NOT want to check			  
    """
    
    if GlobMethods.is_admin():
        return

    tab_rights_features = right_of_admin_of_tab(db_obj, tablename)
    if tab_rights_features == None:
        raise BlinkError(1, 'You have no right to manage table "' + tablename + '".')
    t_rights = tab_rights_features['rights']

    if 'tab' in act:
        tRightArrWant = act['tab']
    else:
        tRightArrWant = ['write']
        
    debug.printx(__name__, "tRightArrWant:" + str(tRightArrWant))
    debug.printx(__name__, "t_rights:" + str(t_rights))

    for rightWant in tRightArrWant:

        if t_rights[rightWant] != 1:
            answer = 'You have no right to ' + rightWant + ' for this table.'
            raise BlinkError(1, answer )

    

    

