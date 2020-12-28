# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
edit LINKS
File:           doc_link.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oVERSION import oVERSION_edit
from blinkdms.code.lib.oDOC import oD_LINK
from blinkdms.code.lib.gui.form import form
from blinkdms.code.lib import oROLE


class plug_XPL(gPlugin):
    '''
     :var self._req_data:
       'id' : VERSION-ID
       'go' : 0,1  
       'ch' : Child Doc ID on update
       'act':
         'new' need 'code'
         'del' delete
         
    '''
  
    obj_ext_lib  = None # extender class

    def register(self):

        idtmp = self._req_data.get('id', 0)
        try:
            self.objid = int(idtmp)
        except:
            self.objid = 0

        self.infoarr['title'] = 'Link Doc'
        self.infoarr['layout'] = 'doc_link'
        self.infoarr['viewtype'] = 'object'
        self.infoarr['objtype'] = 'VERSION'
        self.infoarr['id'] = self.objid
        self.infoarr['obj.id_check'] = 1
        self.infoarr['locrow.show_mo']=1
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT]
        self.infoarr['context.allow'] = ['EDIT']        

    def _do_new(self, db_obj, code):
    
        table_lib = table_cls('DOC')
        ch_id = table_lib.element_get_rcol(db_obj, {'C_ID': code}, 'DOC_ID')
        if not ch_id:
            raise BlinkError(1, 'Doc with ID "' + code + '" not found.')
        
        modlib = oD_LINK.Modify_obj(db_obj, self.doc_id)

        params_use = {
            'C_DOC_ID': ch_id
        }
        dummy = modlib.new(db_obj, params_use)
        self.setMessage('OK', 'Link created.')

    
  
    def _delete_form(self, ch_id):
        pass

    def _delete(self, db_obj, ch_id):
        modlib = oD_LINK.Modify_obj(db_obj, self.doc_id)
        idarr = {'C_DOC_ID':ch_id}
        modlib.delete(db_obj, idarr)
        
        self.setMessage('OK', 'Link deleted.')
    
    def startMain(self):

        db_obj = self._db_obj1
        

        self._html.add_meta('id', self.objid)

        objlib = oVERSION_edit.Mainobj(db_obj, self.objid)
        self.doc_id = objlib.doc_id
        
        parx = self._req_data.get('parx', {})
        go = int(self._req_data.get('go', '0'))
        action = self._req_data.get('act', '')
        self.massdata = {'action': action}
       
        if not objlib.get_current_versid(db_obj):
            raise BlinkError(1, 'This version is not valid for Edit-Mode!')

        if objlib.workflow_is_active(db_obj):
                raise BlinkError(1, 'Workflow is active.')


        if action == 'del':
            ch_id = self._req_data.get('ch', '').strip()
            if ch_id == '':
                raise BlinkError(1, 'Input: linked doc ID is missing.')

            ch_id = int(ch_id)
            
            if go > 0:      
                self._delete(db_obj, ch_id)
                req_data = {
                    'mod': 'doc_edit',
                    'id': self.objid
                     }                
                self.forward_internal_set(req_data)

            else:
                self._delete_form(ch_id)

        if action == 'new' and go > 0:

            if 'code' not in self._req_data:
                raise BlinkError(1, 'Please give a Doc-ID.')
            
            code = self._req_data.get('code', '').strip()
            if code == '':
                raise BlinkError(1, 'Please give a Doc-ID.')

            self._do_new(db_obj, code)

            self._html.setMessage('OK', 'ok')
            req_data = {
                'mod': 'doc_edit',
                'id': self.objid
                 }
            self.forward_internal_set(req_data)
            
        else:
            # self.form_sign(parx)
            pass

    
    def mainframe(self):

        self.sh_main_layout(massdata=self.massdata)
    
 
        
        