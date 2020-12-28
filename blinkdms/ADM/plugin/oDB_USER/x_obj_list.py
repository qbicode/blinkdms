# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
extension for ../obj_list.py
File:           oDB_USER/obj_list.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.obj_list_IF import obj_list_IF, menu_get_index
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.oDB_USER import oDB_USER 

class extend_obj(obj_list_IF):
    
    def __init__(self):
        super().__init__()
        
        
    
    def mod_menu(self, menu):

        ind_mem_func = menu_get_index(menu, 'func')
        if ind_mem_func >= 0:
            menu[ind_mem_func]['submenu'].append({'title': 'add role', 'url': '?mod=ADM/oDB_USER/list_act&action=add_role'})
    

   
   