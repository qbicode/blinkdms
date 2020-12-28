# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
user actions
File:           oUSER_GROUP/actions.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
#from blinkdms.code.lib.tab_abs_sql import Table_sql
from blinkdms.code.lib import obj_mod





class plug_XPL(gPlugin) :  
    '''
     user group actions
     :param: id:  USER_GROUP_ID: only allowed for root !!!
     :param action:
       'add_devs' : add devices
       'del_user' : delete one user from group
     :param ids : if action='del_user' : list of users
        dict: {USER_ID: 1}
    '''

    def register(self) :

            
        self.objid = int(self._req_data.get('id',''))                

        self.infoarr['title']	= 'User Group Actions'
       
        self.infoarr['layout']	= 'ADM/oUSER_GROUP_actions'        
        self.infoarr['id']	= self.objid
        self.infoarr['objtype'] = 'USER_GROUP'
        self.infoarr['viewtype'] = 'object'
              
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]          
        
   
   
    def del_users(self, db_obj, user_ids):
        '''
        remove users from group
        '''
        
        grp_ass_lib = obj_mod.Obj_assoc_mod(db_obj, 'DB_USER_IN_GROUP', self.objid)
        
        for user_id in user_ids:
            idarr= {'DB_USER_ID':user_id}
            grp_ass_lib.delete(db_obj, idarr)
            
        self.setMessage('OK', 'Users removed.')
        

    def startMain(self) :
        
        db_obj  = self._db_obj1
        #db_obj2 = self.db_obj2()
        
        self.data_out = {}

        #if 'parx' not in self._req_data:
        #    self.setMessage('ERROR', 'Input data needed.')   
        #    return
        # parx = self._req_data['parx']
        self.do_forward = 1
        
       
        
        if self._req_data.get('action', 0) == 'del_user' :
            
            user_table ='DB_USER'
            table_lib = table_cls(user_table)
            table_nice = table_lib.nice_name()            
            
            user_ids_dict = self._req_data.get('ids', {}) 
            num_obj = len(user_ids_dict)
            if num_obj <=0:
                self.setMessage('ERROR', 'No objects of type: '+table_nice+' selected.') 
                return                 
            
            if int(self._req_data.get('go', 0)) < 1:
                self.data_out['form'] = {
                    'init': { 'editmode':'edit', 'title':'Delete users from this group?'},
                    'hidden': {
                        "mod": self._mod,
                        "action" :  'del_user',
                        "go": 1,
                        "id": self.objid
                    },
                    'main': [
                        {'title':'Selected Users', 'edit':0, 'val':num_obj }
                    ]
                }
                
                self.data_out['form']['ids'] = {}
                for user_id, flg in user_ids_dict.items():
                    self.data_out['form']['hidden']['ids['+user_id+']']=1
                return            
            
            user_ids = []
            for user_id, flg in user_ids_dict.items():
                user_ids.append(user_id)
            
            self.del_users(db_obj, user_ids)
                    
        if self.do_forward:   
            self._html.forward( '?mod=ADM/obj_one&t=USER_GROUP&id=' + str(self.objid) , 'back to user group')
                
        
    def mainframe(self):

        self.sh_main_layout(massdata = self.data_out)    
