# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
user actions
File:           oDB_USER/actions.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oDB_USER import oDB_USER


class plug_XPL(gPlugin) :  
    '''
     * actions
     :param: id:  DB_USER_ID: only allowed for root !!!
     :param action:
       'add_role' : need parx['role_key']
       'del_role' : need parx['role_key']
       'add_grp'  : need parx['group_id']
     :param parx
       ...
    '''

    def register(self) :
        
        # user_full  = self.infoarr['user.fullname']
        
            
        self.objid = int(self._req_data.get('id',''))                

        self.infoarr['title']	= 'User Actions'
       
        self.infoarr['layout']	= 'ADM/oDB_USER_actions'        
        self.infoarr['id']	= self.objid
        self.infoarr['objtype'] = 'DB_USER'
        self.infoarr['viewtype'] = 'object'
        self.infoarr['role.need'] = ['admin'] # allowed for content-admin
              
        self.infoarr['locrow'] = [
            {'url': 'ADM/home', 'text': 'Home'},
        ]
        
    def act_role_add(self, db_obj, role_id):

        act_lib = oDB_USER.modify_obj(db_obj, self.objid)
        act_lib.add_role(db_obj, role_id)

        self.setMessage('OK', 'Updated.')
        
    def act_role_del(self, db_obj, role_id):

        act_lib = oDB_USER.modify_obj(db_obj, self.objid)
        act_lib.del_role(db_obj, role_id)

        self.setMessage('OK', 'Updated.')    

    def act_group_add(self, db_obj, group_id):

        act_lib = oDB_USER.modify_obj(db_obj, self.objid)
        act_lib.add_group(db_obj, group_id)

        self.setMessage('OK', 'Updated.')

    def startMain(self) :
        
        db_obj = self._db_obj1
        admin = self._session['sesssec']['admin.flag']

        self.objlib = obj_abs('DB_USER', self.objid)
        
        if 'parx' not in self._req_data:
            self.setMessage('ERROR', 'Input data needed.')   
            return
        
        parx = self._req_data['parx']
        
        if self._req_data.get('action', 0) == 'add_role' :
            
            if 'role_key' not in parx:
                self.setMessage('ERROR', 'No Role selected.')
            role_id = parx['role_key']
            self.act_role_add(db_obj, role_id )
            
        if self._req_data.get('action', 0) == 'del_role' :
            
            if 'role_key' not in parx:
                self.setMessage('ERROR', 'No Role selected.')       
            role_id = parx['role_key']
            self.act_role_del(db_obj, role_id )        
            
        if self._req_data.get('action', 0) == 'add_grp' :

                
                if 'group_id' not in parx:
                    self.setMessage('ERROR', 'No Group selected.')     
                    
                group_id = int(parx['group_id'])
                self.act_group_add(db_obj, group_id )              
            
        self._html.forward( '?mod=ADM/obj_one&t=DB_USER&id=' + str(self.objid) , 'back to user')
                
        
    def mainframe(self):

        self.sh_main_layout()    
