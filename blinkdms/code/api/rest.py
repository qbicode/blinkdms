# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
REST interface
File:           rest.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
import json
import sys
import base64
import importlib
import traceback
from flask import session

from blinkdms.conf import config
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.db import db
from blinkdms.code.lib.f_utilities import BlinkError

class MainObj:
    
    page_lib = None
    
    def _reset_sess_vars(self):
        session['loggedin'] = 0
        if not 'sesssec' in session:
            session['sesssec'] = {}                
        session['sesssec']['admin.flag'] = 0  

    def _get_plug_file_info(self, module):
        '''
        create import path and full plugin-file name
        :param string module: e.g. "login" or root/terminal"
        '''

        mod_parts     = module.split('/')
        if mod_parts[0]=='ADM':
            # admin plugin
            plugin_dir     = 'code/plugin/'
            plugin_py_path = 'blinkdms.code.plugin.' 
        else:
            plugin_dir     = 'code/plugin/'
            plugin_py_path = 'blinkdms.code.plugin.'        
        cfgname     = module + '.py'

        cfgname_full= plugin_dir + cfgname
        if not os.path.exists(cfgname_full) :#
            debug.printx(__name__, "ERROR: Modul not found: "+ cfgname_full )
            raise ValueError ('Module "'+ module +'" not found')
        
        # check for sub dirs
       
        import_substr = '.'.join(mod_parts)
        
        imppath =  plugin_py_path + import_substr # old: 'blinkdms.code.plugin.'
        
        return {'imppath':imppath, 'file':cfgname_full}

    def start(self, req_data) :
        '''
        :param string mod: e.g. "login" or root/terminal"
        :resturn: single value or DIC
           'data': {}
           'error': {'key':mess_key, 'text':message, 'stack_str':stack_str}
        '''
        
        mod = req_data['mod']
        result_api={}

        try:
            
            dbid    = config.superglobal['db.std_config_id'] 
            access_config = config.superglobal['db'][dbid]
            db_obj1 = db()
            db_obj1.open( access_config )            
            plug_info = self._get_plug_file_info(mod)
        
            req_data['mod'] = mod   # update mod ...
            
            mod_session_need = 1
            if mod == 'login':
                mod_session_need = 0
                self._reset_sess_vars()             
            
            import_string = plug_info['imppath']
            debug.printx(__name__, "import_plugin: "+ import_string )
            imported_mod = importlib.import_module(import_string)
    
            self.page_lib = imported_mod.plug_XPL(db_obj1, mod)   # FACTORY of class gPlugin()
            
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            message = str(exc_value) 

            err_stack = traceback.extract_tb(exc_traceback)     
            result_api['error'] = { 'key':'ERROR', 'text': message, 'stack_str': repr(err_stack) }
            return result_api
                
        try:    
            self.page_lib._set_session(session,  mod_session_need)
            self.page_lib._set_Superglobal(db_obj1, config.superglobal )
            self.page_lib._set_req_data(req_data)
            self.page_lib.is_rest = 1
        
            self.page_lib.register()
            self.page_lib._init()

            stop      = 0
            error_got = 0
        
            self.page_lib._check_inits() 
            self.page_lib.startMain()
            self.page_lib.mainframe()
            result_api['data'] = self.page_lib.rest_data

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            message = str(exc_value) 
            error_got = 1

            #self._show_error(message)
            #stop = 1
        if error_got:
            
            err_stack = traceback.extract_tb(exc_traceback)
            debug.printx(__name__, "START_PAGE: exc_type:"+ str(exc_type) )
            debug.printx(__name__, "exc_value:"+ str(exc_value) )
            debug.printx(__name__, "exc_traceback:"+ repr(err_stack) )            
            self.page_lib.setMessage('ERROR', message, err_stack=err_stack)
            
        err_mess = self.page_lib.getErrMessage()
        if err_mess is not None:
            result_api['error'] = err_mess        

        return result_api