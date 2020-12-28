# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
show my doc list
File:           doc_list_my.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.plugin.subs import obj_list_show

from blinkdms.code.lib.oDOC import oDOC_VERS
from blinkdms.code.lib.tab_abs_sql import Table_sql


class plug_XPL(gPlugin):
    '''
     :var self._req_data:
    OPTIONAL:
       qs : dict sorting dict
    
    '''

    def register(self) :
        self.infoarr['title'] = 'my doc list'
        self.infoarr['layout']   = 'obj_list'
        self.infoarr['viewtype'] = 'tool'

    def startMain(self) :
        
        db_obj  = self._db_obj1
        db_obj2 = self.db_obj2()
        self.massdata = {}
        
        tablib = oDOC_VERS.Table('EDIT')
        use_table = tablib.table

        user_id = session['sesssec']['user_id']
        my_condition = tablib.search_EDIT_owner(user_id)
       
        
        sql_build_lib = Table_sql(use_table)
        sql_build_lib.reset()
        sql_build_lib.add_condition_full(my_condition)
        sql_build_lib.save_session()

        list_lib = obj_list_show.ShowList(self.massdata, self._req_data)
        list_lib.start(db_obj, db_obj2)


    def mainframe(self):
        self.sh_main_layout(massdata=self.massdata)
    

