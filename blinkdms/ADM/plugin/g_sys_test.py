# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
Admin SYSTEM TEST plugin
.. module::  g_sys_test.py
:copyright:  Blink AG   
:authors:    Steffen Kube <steffen@blink-dx.com>
"""

import os

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib import oGLOBALS




main_tests = [
    'SW_Version',
    'DBVersion',
    'DataDir',
    'WorkDir',
    'email_send_allow'
    
]

class Sys_tests_Main:
    '''
    MIAN tests for ALL app types
        'code' : string code of test
        'key'  : string name of variable key [OPTIONAL]
        'status': 'ok', 'error', 'warn', '?', 'info'
        'nice':   nice name of test
        'val':    value of output
        'notes':  notes
    '''
    
    data_cache = {}
    
    def __init__(self, db_obj):
        
        self._db_obj    = db_obj
        self.data_cache = {}

    def perform_(self, funcname):
        '''
        perform a test
        '''
        func = getattr( Sys_tests_Main, funcname )
        answer = func(self) 
        answer['code'] = funcname
        return answer
        
    # ------------------------------------------------------
    # TESTS, sorted by ALPHABET
    #
    
    def SW_Version(self):

        version = session['sesssec']['SW_Version']
        answer = {
            'key' : 'SW_Version',
            'status': '?',
            'nice':   'SW-Version',
            'val':    version,
            'notes':  'Version of the application'
        }
        if version=='' or version==None:
            answer['status']='error'
        else:
            answer['status']='ok'  
            answer['val'] = version 
        
        return answer  
    
    def DBVersion(self):

        version = oGLOBALS.Methods.get_val(self._db_obj, 'db.version')
        answer = {
            'key' : 'db.version',
            'status': '?',
            'nice':   'db.version',
            'val':    version,
            'notes':  'Database model version'
        }
        if version=='':
            answer['status']='error'
        else:
            answer['status']='ok'  
            answer['val'] = version 
        
        return answer      
    
    def email_send_allow(self):
        
        flag = session['globals'].get('email.send.allow',0)
        
        answer = {
            'key' : 'email.send.allow',
            'status': 'ok',
            'nice':   'email.send.allow',
            'val':    flag,
            'notes':  'Allow System to send emails?'
        } 
        return answer
    
    def DataDir(self):
        
        answer = {
            'status': '?',
            'nice':   'data_path',
            'val':    '?',
            'notes':  ''
        }        
        
        if session['globals'].get('data_path','') == '':
            answer['status']= 'error'
            answer['notes'] = 'data_path not set'
            return answer    

        data_path = session['globals']['data_path']

        answer['val']= data_path 
        
        if not os.path.exists(data_path):
            answer['notes'] = 'data_path not found'
            answer['status']= 'error'
            return answer 
        
        if not os.access(data_path, os.W_OK) :
            answer['notes'] = 'data_path found, but not writeable.'
            answer['status']= 'error'
            return answer            
        
        answer['status']='ok'        
        
        return answer          
        
    def WorkDir(self):
        
        answer = {
            'status': '?',
            'nice':   'work_path',
            'val':    '?',
            'notes':  ''
        }        
        
        if session['globals'].get('work_path','') == '':
            answer['status']= 'error'
            answer['notes'] = 'work_path not set'
            return answer    

        data_path = session['globals']['work_path']

        answer['val']=data_path  
        
        if not os.path.exists(data_path):
            answer['notes'] = 'work_path not found'
            answer['status']= 'error'
            return answer 
        
        if not os.access(data_path, os.W_OK) :
            answer['notes'] = 'work_path found, but not writeable.'
            answer['status']= 'error'
            return answer            
        
        answer['status']='ok'        
        
        return answer        

class plug_XPL(gPlugin) :  
    '''
     * @package g_sys_test.py
     * @author  Steffen Kube (steffen@blink-dx.com)
    :params: 
      "action" :  
         'session_vars' 
         'db_cache'
         
    '''

    def register(self) :
        self.infoarr['title']	= 'System check'
       
        self.infoarr['layout']	= 'ADM/g_sys_test'        
        self.infoarr['locrow']  = [ {'url':'ADM/home', 'text':'Home'} ]
        self.infoarr['role.need'] = ['admin'] # allow to admin group
    
    def _build_table(self, data):
        '''
        build one table
        '''
        data_rows=[]
        one_table =  {
          'header': {
             'title' : 'System Check Overview',
          },
         'cols' : [],  # OPTIONAL
         'data' : data_rows,   # list of rows                
        }   
        
        outcols = [
            'code',
            'status',
            'nice',
            'val',
            'notes'            
        ]
        
        for row in data:
            
            onerow = []
            for key in outcols:
                onerow.append (row[key] )
            
            data_rows.append( onerow )
            
        self.massdata['table'] = one_table
  

    def startMain(self) :
        
        self.massdata = {}
        
        db_obj = self._db_obj1
        
        result_list = []
        
        main_test_lib = Sys_tests_Main(db_obj)
        for one_test in main_tests:
            result = main_test_lib.perform_(one_test)
            result_list.append(result)        
       
        self._build_table(result_list)

    def mainframe(self):
        self.sh_main_layout(massdata = self.massdata )    
