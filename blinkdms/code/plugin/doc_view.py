# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
view a document
File:           doc_view.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oVERSION import oVERSION_active
from blinkdms.code.lib.oDOC import oDOC_VERS
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
        do_check_id = 1
        self.err_of_register = None
        
        if 'd_id' in self._req_data:
            doc_id = self._req_data['d_id']
            try:
                doc_id = int(doc_id)
            except:
                doc_id = 0
            if doc_id:
                db_obj = self._db_obj1
                doc_vers_lib = oDOC_VERS.Table('ACTIVE')
                self.objid = doc_vers_lib.get_version_id(db_obj, doc_id)
                if not self.objid:
                    self.err_of_register = {
                        'doc_id':doc_id 
                    }
                    do_check_id = 0

                
        if not self.objid:
            
            idtmp = self._req_data.get('id', 0)
            try:
                self.objid = int(idtmp)
            except:
                self.objid = 0        

        self.infoarr['title'] = 'view document'
        self.infoarr['layout'] = 'doc_view'
        self.infoarr['objtype'] = 'VERSION'
        
        if do_check_id:
            self.infoarr['viewtype'] = 'object'
            self.infoarr['id'] = self.objid
            self.infoarr['obj.id_check'] = 1
        else:
            self.infoarr['viewtype'] = 'tool'
            
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT, oROLE.ROLE_KEY_VIEW]
        self.infoarr['context.allow'] = ['ACTIVE']        

   

    def startMain(self):
        
        db_obj = self._db_obj1
        
        self.massdata = {}
        self.is_released = 0
        action = self._req_data.get('act', '')   
        pos    = int(self._req_data.get('pos', '0'))
               

        if self.err_of_register != None:
            doc_id = self.err_of_register['doc_id']
            doc_obj = obj_abs('DOC', doc_id)
            if not doc_obj.obj_exists(db_obj):
                raise BlinkError(1, 'Document with internal-ID ' + str(doc_id) + ' is unknown.')
            nicename = doc_obj.obj_nice_name(db_obj)
            raise BlinkError(2, 'Document "' + nicename + '" has no valid version.')            

        active_lib = oVERSION_active.Mainobj(self.objid)
        if not active_lib.version_exists(db_obj):
            raise BlinkError(1, 'This version is not an ACTIVE version!')

        objlib      = oVERSION.Mainobj(self.objid)
        features    = objlib.features(db_obj)
        self.doc_id = features['vals']['DOC_ID']

        
        if action == 'down':
            if not pos:
                raise BlinkError(1, 'Input: pos missing.') 
            
            doc_type = self._req_data.get('type', '')
            gui_lib = oVERSION_show.Parts(db_obj, self._html, self.objid)
            gui_cont_file = gui_lib.download(db_obj, pos, doc_type)
            
            self.infoarr['gui'] = -1  # for download
            self.infoarr['gui.cont.type'] ='file'
            self.infoarr['gui.cont.file'] = gui_cont_file            
            
            return        
        
        #### general section
        
        #if objlib.is_released(db_obj):
        #    self.is_released = 1        
        
        gui_lib = oVERSION_show.Parts(db_obj, self._html, self.objid)

        gui_lib.show_all(db_obj, 'ACTIVE')
        
        self.massdata = gui_lib.get_mass_data()
        
    
    def mainframe(self):

        self.sh_main_layout(massdata=self.massdata)
    