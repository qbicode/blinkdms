# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
dictionary help
File:           dict_help.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

def get_value(mydict, key):
    """
    transform dict-key-val into an EMPTY string, if not exists or None
    """
    if key not in mydict:
        return ''
    
    if mydict[key] == None:
        return ''
    
    return mydict[key]

def has_value(mydict, key):
    """
    transform dict-key-val into an EMPTY string, if not exists or None
    :return: 0 or 1
    """
    if key not in mydict:
        return 0
    
    if mydict[key] == None:
        return 0
    
    # check for empty string
    if type(mydict) == str and mydict[key]=='':
        return 0
    
    return 1