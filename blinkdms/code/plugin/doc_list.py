# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
search
File:           doc_list.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import sys

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.plugin.subs import obj_list_show


class plug_XPL(gPlugin):
    '''
     :var self._req_data:
    OPTIONAL:
       qs : dict sorting dict
    
    '''

    def register(self) :
        self.infoarr['title']	 = 'Search'
        self.infoarr['layout'] = 'obj_list'
        self.infoarr['viewtype'] = 'tool'

    def startMain(self) :
        
        db_obj  = self._db_obj1
        db_obj2 = self.db_obj2()
        self.massdata = {}
        list_lib = obj_list_show.ShowList(self.massdata, self._req_data)
        list_lib.start(db_obj, db_obj2)


    def mainframe(self):
        self.sh_main_layout(massdata=self.massdata)
    

