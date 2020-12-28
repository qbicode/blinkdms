# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
search
File:           doc_new.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.gui.form import form

from blinkdms.code.lib.oDOC import oDOC_lev2
from blinkdms.code.lib.oDOC_TYPE import oDOC_TYPE
from blinkdms.code.lib.oPROJ     import oPROJ
from blinkdms.code.lib import oROLE




class plug_XPL(gPlugin) :  
    '''
    :param self._req_data:
    REQUIRED
      proj_id - PROJ_ID
      go : 0,1
      parx : document attributes from user
        NAME
        DOC_TYPE_ID
       
    OPTIONAL:
    
    '''
  
    obj_ext_lib  = None # extender class

    def register(self) :
        
        layout = 'doc_new'
        self.proj_id = int(self._req_data.get('proj_id', 0))  # cast to INT
        if not self.proj_id:
            layout = 'folder_sel'

        self.infoarr['title']    = 'New document'
        self.infoarr['layout']   = layout
        self.infoarr['viewtype'] = 'tool'
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT]
        self.infoarr['context.allow'] = ['EDIT']        
        
    def _form(self, db_obj):
        
        proj_lib = oPROJ.mainobj(self.proj_id) 
        proj_path_str = proj_lib.get_path_str(db_obj)
        #self._html.add_meta('proj.path_str', proj_path_str)        
        
        types = oDOC_TYPE.Table.get_all_types(db_obj)
        sel_type = []
        for row in types:
            sel_type.append([row['id'], row['name']])
        
        fields = [
         {                'title': 'Folder', 'object': 'text', 'val': proj_path_str, 'edit':0 },
         {'name': 'NAME', 'title': 'Title', 'object': 'text', 'val': ''},
         {'name': 'DOC_TYPE_ID', 'title': 'Type', 'object': 'select', 'val': '', 'inits': sel_type},
        ]
        
        hidden = {
            "mod": self._mod,
            "action": 'profile',
            'proj_id': self.proj_id
        }
        
        self.form_obj = form({"submit.text":'Create'}, hidden, 0)
        self.form_obj.set_form_defs(fields)

    def create_doc(self, db_obj, parx, proj_id):
        '''
        update profile
        '''
        params = {
            'vals': parx,
            'proj_id': proj_id
        }
        
        act_lib = oDOC_lev2.Modify_obj(db_obj)
        v_id = act_lib.new(db_obj, params)

        self.setMessage('OK', 'Created.')
        
        return v_id
        
    def startMain(self):
        
        db_obj = self._db_obj1
        
        self.proj_id = int(self._req_data.get('proj_id', 0))  # cast to INT
        
        if not self.proj_id:
            # show the project selector ...

            req_data = {
                'mod':      'folder_sel',
                'back_key': 'DOC.new'
            }
            self.forward_internal_set(req_data)
            return
        
        

        self._form(db_obj)
        
        if int(self._req_data.get('go', 0)) > 0:
  

            values_new = self.form_obj.check_vals(self._req_data.get('parx', {}))
            v_id = self.create_doc(db_obj, values_new, self.proj_id)
            
            req_data = {
                'mod': 'doc_edit',
                'id': v_id
            }
            self.forward_internal_set(req_data)
            return            

    def mainframe(self):

        form_data = self.form_obj.get_template_data()
        self.sh_main_layout(massdata={'form': form_data})
    
 
        
        