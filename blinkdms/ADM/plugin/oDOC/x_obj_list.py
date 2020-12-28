# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
extension for ../obj_list.py
File:           oDOC/obj_list.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.obj_list_IF import obj_list_IF, menu_get_index
from blinkdms.code.lib.main_imports import *
#from blinkdms.code.lib.oDB_USER import oDB_USER

class extend_obj(obj_list_IF):
    
    def __init__(self):
        super().__init__()
        self.version = '1.1X'

    def mod_menu(self, menu):
       
        ind_mem_func = menu_get_index(menu, 'func')
        if ind_mem_func >= 0:
            menu[ind_mem_func]['submenu'].append({'title': 'change owner', 'url': '?mod=ADM/oDOC/list_act&action=chown'})
   