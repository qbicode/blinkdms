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
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.oUSER_GROUP import oUSER_GROUP
from blinkdms.code.lib import oROLE


class extend_obj(obj_one_IF):
    
    def init(self, db_obj):
        # init after set_vars
        
        user_lib = oDB_USER.mainobj(session['sesssec']['user_id'])
        self.is_context_admin = user_lib.has_role(db_obj, oROLE.ROLE_KEY_ADMIN)    
    
    def mod_menu(self, menu):
 
        adminflag = session['sesssec']['admin.flag']
        
        look=['object']
        ind_mem={}
        
        ind=0
        for row in menu:
            for key in look:
                if row['m_name']==key:
                    ind_mem[key] = ind
                     
            ind = ind + 1
            
        if self.is_context_admin:
            if 'object' in ind_mem:
                menu[ind_mem['object']]['submenu'].append( {'title':'change password', 'url':'?mod=ADM/oDB_USER/myprofile&id='+ str(self.objid) } )
                
                
                        
    def page_bottom(self, db_obj,  db_obj2, massdata):
        """
        user groups
        """
        
        group_obj = obj_abs('USER_GROUP', 0)
        
        self._html.add_meta('bot.include', 1)

        objid = self.objid
        
         

        user_lib = oDB_USER.mainobj(objid)
        groups = user_lib.get_groups(db_obj)
        
        
        out_list = []
        for group_id in groups:
            group_obj.set_objid(group_id)
            col_data = group_obj.main_feat_all(db_obj)
            
            typex   = col_data.get('TYPEX','')
            one_row = [group_id, col_data['NAME'], typex ]
            out_list.append(one_row)
        
        self._html.add_meta('bot_groups', out_list)

        group_ist = oUSER_GROUP.Table.non_single_groups_active(db_obj)

        
        grp_form_info = [
            {
                'title': 'Select Group',
                'name': 'parx[group_id]',
                'object': 'select',
                'inits': group_ist
            }
        ]
        
        self._html.add_meta('bot_grp_form', grp_form_info)          
        
        # get USER roles
        # TBD: code later
        if 1:
            
            roles = user_lib.get_role_names(db_obj)

            out_list = []
            for row in roles:

                role_key = row[0]
                one_row = [role_key, row[1]]
                out_list.append(one_row)
            
            self._html.add_meta('bot_roles', out_list)   
            
            #
            # get all roles
            #
            roles = oROLE.Table.get_all_roles_nice(db_obj)
       
        
            role_list = []
            for row in roles:
                one_row = (row['KEY'], row['NAME'])
                role_list.append(one_row)
            
            role_table_info = [
                {
                    'title': 'Select Role',
                    'name': 'parx[role_key]',
                    'object': 'select',
                    'inits': role_list
                }
            ]
            
            self._html.add_meta('bot_roles_all', role_table_info) 
        
    def update_pre(self, db_obj):
        '''
        prevent other users from changing root parameters ...
        '''
        
        old_vals = self._obj_features['vals']  
        if old_vals['NICK'] =='root':
            if session['sesssec']['user']!='root':
                raise BlinkError (1, 'Only root can change its parameters!')
            
# ------------------------------
        
class extend_new(obj_new_IF):
    
    def init(self, db_obj):
        '''
        check initial data
        '''
        pass
    
    def get_columns(self):
        
        columns_show = [
         {'col': 'x.NICK'},
         {'col': 'x.FULL_NAME'},
         {'col': 'x.EMAIL'}
        ]  
        return columns_show        
    
    def check_data(self, db_obj):
        '''
        check and modify data
        '''   
 
        # create password
        user_lib = oDB_USER.mainobj(0)
        
        self.params['x.EMAIL'] = self.params['x.EMAIL'].strip()
        if self.params['x.EMAIL'] == '':
            raise BlinkError(1,'No email given.')
        
        
        password = user_lib.create_user_pw()
        pw_raw   = user_lib.hash_pw(password)
        
        self.params['x.PASS_WORD'] =  pw_raw