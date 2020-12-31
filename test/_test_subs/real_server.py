# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
use the real FLASK server
File:           real_server.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

import unittest

from test._test_subs import jsonrpc
from test._test_subs import rest
# from test._test_subs import utilities
# from blinkdms.conf import conf_unittest

class RPC_result_Error(Exception):
    pass

class RPC_unknow_Error(Exception):
    pass

class Blink_UT_Real_Cls(unittest.TestCase):
    
    url   =''
    user  = ''     
    
    def setUp(self):
        
        username     = self.user
        
        self.rest_server = rest.Rest_help(  )
        self.rest_server.crea_empty_session()  

        login_argu={}

        result = self.rest_server.login(login_argu, username)


    def print_debug(self, text):
        
        print ('UnitTest-Print: '+ text )
    
    def rpc_call(self, method, argu):
        response = self.rest_server.send_it(method, argu)
        
        if 'error' in response:
            raise RPC_result_Error( response['error'] )        
        
        if 'data' not in response:
            raise RPC_unknow_Error('Unknown Error occurred: '+str(response) )
        
        result = response['data']
        return result

    def tearDown(self):
        self.rest_server.logout()