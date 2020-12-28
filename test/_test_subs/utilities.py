# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
unit test utilities
File:           utilities.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import random

def create_password():
    """
    create strong password
    """     

    chars = "abcdefghijklmnopqrstuvwxyziABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890^?!?$%&/()=?+#*~;:_,.-<>|"
    password = ""
    length   = 12
    while len(password) != length:
        password = password + random.choice(chars)
        if len(password) == length:
            break 
    return password  

def create_hash(length):
    """
    create hash, no special chars
    """     

    chars = "abcdefghijklmnopqrstuvwxyziABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    password = ""
    while len(password) != length:
        password = password + random.choice(chars)
        if len(password) == length:
            break 
    return password 

def print_debug(text):
    
    print ('UnitTest-Print: '+ text )