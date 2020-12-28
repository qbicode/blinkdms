# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"
"""
methods to handle dynamic import of modules
File:           f_module_helper.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
    
import os
import importlib
import inspect
from blinkdms.code.lib.debug import debug

def check_module(relpath, is_abspath=0):
    """
    look for extension 
    :param relpath: starting from "blinkapp/code" : e.g. "plugin/ + self.table +'/' + 'obj_one'
    :param is_abspath: set 0, if is this path located in "code/"
    :return: imported_mod or None
    """
    
    #obj_ext_lib = None
    if not is_abspath:
        relpath = 'code/' + relpath
    else:
        pass
    
    extfile = relpath +'.py'
    imported_mod  = None
    import_string = ''
    
    if os.path.exists(extfile) :
        mod_parts     = relpath.split('/')
        import_substr = '.'.join(mod_parts)
        import_string = 'blinkdms.' + import_substr
        imported_mod = importlib.import_module(import_string)
    
    daddy = inspect.stack()[2][3]
    debug.printx( __name__, 'check_module(1): caller: '+str(daddy)+ ' in:'+relpath+' output:'+ str(imported_mod) + ' import_string: ' + str(import_string) )   
        
    return imported_mod


def module_has_class(module, classname):
    """
    check, if module has class
    """
    
    temp = inspect.getmembers(module)
    
    found=0
    for row in temp:
        
        chunk=''
        tmp_split = str(type(row[1])).split(' ')
        part0 = tmp_split[0]
        if part0[0:1]=='<':
            chunk = part0[1:]    
        if chunk=='class':
            class_loop = row[0]
            if classname == class_loop:
                found=1
                break
    
    return found

def class_has_method(module, method):
    
    has_methods = inspect.getmembers(module, inspect.isfunction)
    answer = 0
    if method in has_methods:
        answer = 1   
        
    return answer