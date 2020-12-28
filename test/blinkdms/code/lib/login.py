# TBD: rewrite this test ...
import sys
#import os
#import json
#import random
#import hashlib
import time
#from flask import session

#from blinkdms.conf  import config
# from blinkapp.code.lib.main_imports import *

from test._test_subs import rest

"""
UnitTest
"""
if __name__ == '__main__':

    rest_lib = rest.Rest_help()
    rest_lib.crea_empty_session()
    
    
    argu = {  }
    username = "test"
    pw='1234'
    
    result = rest_lib.login(argu, username, pw)
    print ("LOGIN: "  + str(result) )
    
    # bad
    username = "test"
    pw='1234xx'   
    
    for i in range(7):
        message=''
        try:
            result='FAIL'
            result = rest_lib.login(argu, username, pw)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            message = str(exc_value) 
        print ("LOGIN: "  + str(result) + ' mess:'+ message)    
    
    
    print ("OK")