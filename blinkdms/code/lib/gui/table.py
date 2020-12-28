# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
create simple table struct: table_simple_STRUCT (see table.html)
.. module::  table.py
:copyright:  Blink AG   
:authors:    Steffen Kube <steffen@blink-dx.com>
"""
import os
#from blinkapp.code.lib.main_imports import *

class Table:

    @staticmethod
    def list2table(list_in):
        '''
        produce table_simple_STRUCT
        '''

        table_simple={}
        table_simple['data']=[]
        i=0
        for row in list_in:
            if not i:
                table_simple['cols'] = row
            else:
                table_simple['data'].append(row)
            i=i+1
        return table_simple
            
        
