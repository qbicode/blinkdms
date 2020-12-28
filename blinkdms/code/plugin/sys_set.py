# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
system settings for user
File:           sys_set.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin


class plug_XPL(gPlugin) :  
    '''
    :param _req_data:
       'context': ACTIVE, EDIT
    '''

    def register(self):

        self.infoarr['title'] = 'Home'
        self.infoarr['layout'] = 'empty'


    def startMain(self) :
        # get device num and so on
        
        db_obj = self._db_obj1
        
        debug.printx(__name__, "parx:" + str(self._req_data))

        if self._req_data.get('context', '') != '':
            context = self._req_data['context']
            session['sesssec']['my.context'] = context
            

        req_data = {
            'mod': 'home',
        }
        self.forward_internal_set(req_data)        
        
    def mainframe(self):

        db_obj = self._db_obj1
        massdata= {}

        self.sh_main_layout()
