# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
interface for   
- lib/tab_abs_sql.py (uses Table_sql_IF)

File:           obj_sql_IF.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
    
class Table_sql_IF:
    
    table = ''
    
    def func_wildcard_rep(self, name):
        # replace % by *
        return name.replace('*','%')
    
    def get_alias_cond(self, db_obj, alias, one_query):
        # return string (condition)
        raise NotImplementedError('Alias not implemented')
