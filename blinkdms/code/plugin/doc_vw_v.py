# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
view all doc versions as list

File:           doc_vw_v.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oDOC import oDOC
from blinkdms.code.lib import oROLE




class plug_XPL(gPlugin):
    '''
     :var self._req_data:
       'd_id' doc_ID
       
    '''
  
    obj_ext_lib  = None # extender class

    def register(self):

        self.objid = 0
       
        
        idtmp = self._req_data.get('d_id', 0)
        try:
            self.objid = int(idtmp)
        except:
            self.objid = 0        

        self.infoarr['title']  = 'view all document versions'
        self.infoarr['layout'] = 'doc_vw_v'
        self.infoarr['objtype'] = 'DOC'

        self.infoarr['viewtype'] = 'object'
        self.infoarr['id'] = self.objid
        self.infoarr['obj.id_check'] = 1
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT]
        self.infoarr['context.allow'] = ['EDIT']        

   

    def startMain(self):
        
        db_obj = self._db_obj1
        
        self.massdata = {}

        self._html.add_meta('doc_id', self.objid)

        objlib = oDOC.Mainobj(self.objid)
        version_ids = objlib.all_versions(db_obj)
        
        out_list = []
        
        for v_id in version_ids:

            v_lib   = oVERSION.Mainobj(v_id)
            v_feats = v_lib.features(db_obj)
      
            row = {'v_id':v_id, 'title':v_feats['vals']['NAME'], 
                   'v':v_feats['vals']['VERSION'], 'valid_date':v_feats['vals']['VALID_DATE'] }
            out_list.append(row)
        
        data_table = {}
        data_table = {'header': {'title': 'Audit log'}, 'data': [], 'cols': []}
        data_table['opt'] = {
          'col_t': [
            {'type':'but_link', 'icon':'download', 'url': '?mod=doc_view_a&id='  }
            ]
        }
        data_table['cols'] = ['#','Version', 'Valid_date']     
        data_table['data'] = out_list
        
        self.massdata['vers_list'] = data_table
    
    def mainframe(self):

        self.sh_main_layout(massdata=self.massdata)
    