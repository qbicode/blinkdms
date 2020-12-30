'''
Content-Admin home (NOT root)
'''
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib import tab_info

import sys

class plug_XPL(gPlugin) :  
    '''
     * Content-Admin home plugin
     * @package homec.inc
     * @author  Steffen Kube (steffen@blink-dx.com)
    :param action: 'set.sess_var'
    :param parx: 
        'context.EDIT.admin.active' : 0,1 (if action=='set.sess_var')
    '''

    def register(self):
        self.infoarr['title'] = 'Content-Admin home'
        self.infoarr['layout'] = 'ADM/homec'
        self.infoarr['role.need'] = ['admin'] # allowed for content-admin
        self.infoarr['locrow'] = [{'url': 'ADM/homec', 'text': 'Home'}]

    def startMain(self) :
        
        action =  self._req_data.get('action', '')
        if action=='set.sess_var':
            parx =  self._req_data.get('parx', {})
  
            keyx = 'context.EDIT.admin.active'  
            if keyx in parx:
                flag = int(parx[keyx])
                session['sesssec'][keyx] = flag
        
    def mainframe(self):
        
        db_obj = self._db_obj1

        # some_tables
        sel_tables_raw = [
            'DB_USER',
            'USER_GROUP',
            'DOC_TYPE',
            'SYS_A_LOG'
            #'DOC_VERS_ACTIVE',
            #'DOC_VERS_EDIT',
            #'VERSION'
        ]
        
        some_tables = []
        for table in sel_tables_raw:
            tablib = table_cls(table)
            table_nice  = tablib.nice_name()            

            row = {'t':table, 'nice': table_nice}
            some_tables.append(row)

        self._html.add_meta('some_tables', some_tables)
        
        keyx = 'context.EDIT.admin.active' 
        flag = session['sesssec'].get(keyx,0)
        self._html.add_meta(keyx, flag)
        
        self.sh_main_layout()  
