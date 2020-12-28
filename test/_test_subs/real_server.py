# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
use the real HUB server
File:           real_server.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

import unittest

from test._test_subs import jsonrpc
from test._test_subs import utilities
from blinkapp.conf import conf_unittest

class RPC_result_Error(Exception):
    pass

class RPC_unknow_Error(Exception):
    pass

class Blink_UT_Real_Cls(unittest.TestCase):
    
    url   =''
    user  = ''
    device= ''       
    
    def setUp(self):
        
        username     = self.user
        device_serial= self.device
        
        hub_scope =  conf_unittest.ut_conf['test.scope']
        
        self.jsonrpc_server = jsonrpc.Jsonrpc_help( hub_scope )
        self.jsonrpc_server.crea_empty_session()  
        
        login_type='user'
        if device_serial!='':
            login_type='device'
        
        login_argu={}
        if username=='': 
            username  ='erp-importer' 
        
        if conf_unittest.ut_conf['test.scope']=='hubd':
            login_argu['cid'] =  conf_unittest.ut_conf['test.url']['hubd.cid']
            
        if login_type=='user':   
            result = self.jsonrpc_server.login(login_argu, username)
        else: 
            result = self.jsonrpc_server.login_dev(login_argu, device_serial, pw='' )
        
        a = 1

    def print_debug(self, text):
        
        print ('UnitTest-Print: '+ text )
    
    def rpc_call(self, method, argu):
        response = self.jsonrpc_server.send_it(method, argu)
        
        if 'error' in response:
            raise RPC_result_Error( response['error'] )        
        
        if 'result' not in response:
            raise RPC_unknow_Error('Unknown Error occurred: '+str(response) )
        
        result = response['result']
        return result

    def tearDown(self):
        self.jsonrpc_server.logout()