# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
show open tasks
File:           doc_rv_list.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oDOC import oDOC_VERS
from blinkdms.code.lib.oVERSION import oVERSION_edit


class plug_XPL(gPlugin) :  
    '''
     :var self._req_data:
      REQUIRED

    
    ''' 
  
    obj_ext_lib  = None # extender class

    def register(self) :

        self.infoarr['title'] = 'Show open tasks'
        self.infoarr['layout'] = 'doc_rv_list'
        self.infoarr['viewtype'] = 'tool'
        
  
        
    def startMain(self) :
        
        db_obj = self._db_obj1

        doc_lib = oDOC_VERS.Table('EDIT')
        #usetable = doc_lib.table
 
        version_user_lib = oVERSION_edit.VersionsOfUser(session['sesssec']['user_id'])

        sql_from = version_user_lib.get_sql_from_open_versions(db_obj)
    
        sql_cmd = "count(x.VERSION_ID) from " + sql_from
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        objcnt_sel = db_obj.RowData[0]

        self.massdata = {}
        
        if objcnt_sel:

            cols = ['x.VERSION_ID', 'x.C_ID', 'x.VERSION', 'x.NAME', 'x.NOTES']
            self.massdata['header'] = cols

            cols_text = ','.join(cols)
            sql_cmd = cols_text + " from " + sql_from

            self.massdata['data'] = []
            db_obj.select_tuple(sql_cmd)
            while db_obj.ReadRow():
                row_data = db_obj.RowData
                self.massdata['data'].append(row_data)

    def mainframe(self):

        self.sh_main_layout(massdata=self.massdata)
    
 
        
