# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
extension for ../obj_one.py
File:           DB_USER/obj_one.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.obj_one_IF import obj_one_IF, obj_new_IF
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.oUSER_GROUP import oUSER_GROUP



class extend_obj(obj_one_IF):
    
   
    
         
    def page_bottom(self, db_obj, db_obj2, massdata):
        """
        user groups
        """

        
        self._html.add_meta('bot.include',1)  
        
        grp_lib = oUSER_GROUP.Mainobj(self.objid)
        
        groups = grp_lib.get_users(db_obj)
        
        user_obj = obj_abs('DB_USER', 0)
        
        out_list = []
        for user_id in groups:
            user_obj.set_objid(user_id)
            col_data = user_obj.main_feat_all(db_obj)

            one_row = [user_id, col_data['FULL_NAME'] ]
            out_list.append(one_row)
        
        self._html.add_meta('bot_users', out_list)  
        
                         