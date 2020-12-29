# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
view an ARCHIVED  document-version
- all versions possible, also EDIT and ACTIVE version ...
File:           doc_view_a.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oVERSION import oVERSION
# from blinkdms.code.lib.oDOC import oDOC_VERS
from blinkdms.code.lib import oROLE

from blinkdms.code.plugin.subs import oVERSION_show



class plug_XPL(gPlugin):
    '''
     :var self._req_data:
       'id' : VERSION-ID
       'd_id' doc_ID
       'act'
          'down' : needs 'pos'
       'pos' : INT pos of download doc
    '''
  
    obj_ext_lib  = None # extender class

    def register(self):

        self.objid = 0
       
        
        idtmp = self._req_data.get('id', 0)
        try:
            self.objid = int(idtmp)
        except:
            self.objid = 0        

        self.infoarr['title']  = 'view document ARCHIVE'
        self.infoarr['layout'] = 'doc_view'
        self.infoarr['objtype'] = 'VERSION'

        self.infoarr['viewtype'] = 'object'
        self.infoarr['id'] = self.objid
        self.infoarr['obj.id_check'] = 1
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT]
        self.infoarr['context.allow'] = ['EDIT']        

   

    def startMain(self):
        
        db_obj = self._db_obj1
        
        self.massdata = {}
        self.is_released = 0
        action = self._req_data.get('act', '')   
        pos    = int(self._req_data.get('pos', '0'))

        # objlib = oVERSION.Mainobj(self.objid)
      

        if action == 'down':
            if not pos:
                raise BlinkError(1, 'Input: pos missing.') 
            
            doc_type = self._req_data.get('type', '')
            gui_lib = oVERSION_show.Parts(db_obj, self.objid, doc_type)
            gui_cont_file = gui_lib.download(db_obj, pos)
            
            self.infoarr['gui'] = -1  # for download
            self.infoarr['gui.cont.type'] ='file'
            self.infoarr['gui.cont.file'] = gui_cont_file            
            
            return        
        
        #### general section
       
        self._html.add_meta('is_arch_view', 1)
        
        gui_lib = oVERSION_show.Parts(db_obj, self._html, self.objid)
        
        doc_id = gui_lib.get_doc_id()
        self._html.add_meta('doc_id', doc_id)

        gui_lib.show_all(db_obj)
        
        self.massdata = gui_lib.get_mass_data()
        
    
    def mainframe(self):

        self.sh_main_layout(massdata=self.massdata)
    