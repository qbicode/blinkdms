# TBD: rewrite this test ...

import os
import json
import random
import hashlib
import time
from flask import session

from blinkapp.conf  import config
# from blinkapp.code.lib.main_imports import *

from test._test_subs import jsonrpc

"""
UnitTest
"""
if __name__ == '__main__':

    jsonrpc_lib = jsonrpc.Jsonrpc_help()
    jsonrpc_lib.crea_empty_session()
    
    
    argu = {  }
    username = "root" #"test.bad" # can NOT read object data
    
    result = jsonrpc_lib.login(argu, username)
    print ("LOGIN: "  + str(result) )
    
    argu = {'argu': {'hallo':'version'} } # gGetVersion
    result = jsonrpc_lib.send_it("gGetVersion", argu)
    print ("version: "  + str(result) )
    
    argu = {'t': 'DB_USER', 'id':1 }
    result = jsonrpc_lib.send_it("gObj_getParams", argu)        
    print ("RESULT: "  + str(result) )
    
    argu = {'t': 'DEVICE', 'name':'BOX3' }
    result = jsonrpc_lib.send_it("gObj_getParams", argu)        
    print ("RESULT: "  + str(result) )    
    
    argu = {'t': 'DEVICE', 'name':'BOX_XXX_BAD' }
    result = jsonrpc_lib.send_it("gObj_getParams", argu)        
    print ("RESULT: "  + str(result) ) 
    
    
    username = "erp-importer"  # can  read object data
    result = jsonrpc_lib.login(argu, username)
    print ("LOGIN: "  + str(result) )    
    
    argu = {'t': 'DB_USER', 'id':1 }
    result = jsonrpc_lib.send_it("gObj_getParams", argu)        
    print ("RESULT: "  + str(result) )    
    
    argu = {'t': 'DEVICE', 'name':'BOX3' }
    result = jsonrpc_lib.send_it("gObj_getParams", argu)        
    print ("RESULT: "  + str(result) )    
    
    print ("OK")