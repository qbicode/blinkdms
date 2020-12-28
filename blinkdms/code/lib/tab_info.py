# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
general info about all database tables
File:           tab_info.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
from blinkdms.code.lib.main_imports import *


def get_BO_tables(db_obj):
        
    sql_cmd = "TABLE_NAME from CCT_TABLE where TABLE_TYPE='BO' order by NICE_NAME"
    db_obj.select_tuple(sql_cmd)
    all_data = []
    while db_obj.ReadRow():
        table_loop = db_obj.RowData[0]       
        all_data.append(table_loop)        
    
    return all_data

def get_ALL_tables(db_obj):
        
    sql_cmd = "TABLE_NAME from CCT_TABLE order by NICE_NAME"
    db_obj.select_tuple(sql_cmd)
    all_data = []
    while db_obj.ReadRow():
        table_loop = db_obj.RowData[0]       
        all_data.append(table_loop)        
    
    return all_data