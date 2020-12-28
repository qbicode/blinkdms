'''
ROOT home
'''
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib import tab_info

from blinkdms.code.lib.oDB_USER import oDB_USER


class plug_XPL(gPlugin) :  
    '''
     * ROOT home plugin
     * @package home.inc
     * @author  Steffen Kube (steffen@blink-dx.com)
    '''

    def register(self) :

        self.infoarr['title']	= 'Admin home'
        self.infoarr['layout'] = 'ADM/home'
        self.infoarr['locrow'] = [{'url': 'ADM/home', 'text': 'Home'}]

    def route(self, db_obj):
        '''
        if USER is not ROOT => forward to 'mod':'ADM/homec'
        '''
        output = {}        
        user_id = session['sesssec']['user_id']
        user_lib = oDB_USER.mainobj(user_id)
        if not user_lib.is_admin(db_obj):
            output= {
                'mod':'ADM/homec'
            }
        return output
    
    def startMain(self) :
        pass
        
    def mainframe(self):
        
        db_obj  = self._db_obj1
        
        # tables = ['DB_USER', 'USER_GROUP'] #, ROLE
        
        # get all BO
        tables = tab_info.get_ALL_tables(db_obj)

        meta_tables = []
        for table in tables:
            tablib = table_cls(table)
            table_nice  = tablib.nice_name()            

            row = {'t':table, 'nice': table_nice}
            meta_tables.append(row)
            
        self._html.add_meta('tables', meta_tables)
        
        # some_tables

        sel_tables_raw = [
            'DB_USER',
            'USER_GROUP',
            'DOC_TYPE',
            'DOC_VERS_ACTIVE',
            'DOC_VERS_EDIT',
            'VERSION'
        ]
        
        some_tables = []
        for table in sel_tables_raw:
            tablib = table_cls(table)
            table_nice  = tablib.nice_name()            

            row = {'t':table, 'nice': table_nice}
            some_tables.append(row)

        self._html.add_meta('some_tables', some_tables)

        
        self.sh_main_layout()  
