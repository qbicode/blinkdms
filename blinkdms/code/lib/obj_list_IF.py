# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
interface for   
- lib/obj_list.py
- table_out.py
- obj_list_sub.py
- lib/tab_abs_sql.py (uses Table_sql_IF)

File:           obj_list_IF.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.tab_abs_sql import Table_sql
from flask import session

class Sec_table_sql(Table_sql):
    """
    secure SQL builder
    - only show objects of the MDO !
    """
    
    def __init__(self, tablename):
        super().__init__(tablename)
        
        one_query_cond = self._get_def_cond()
        
        if not self.cond_exists(one_query_cond):
            # not exists set condition ...
            self.add_condition(one_query_cond, 1)

        
    def _get_def_cond(self):
        
        # difference between SERVICE and EU
        
        one_query_cond = {}

        if self.tablename=='DB_USER':
            # special for DB_USER
            one_query_cond =   {
                'col':'x.DB_USER_ID', 
                'op':'IN',
                'val': '(select DB_USER_ID from DB_USER_IN_GROUP where USER_GROUP_ID=' + str(mdo_grp_id)+')'
            }           
        return one_query_cond
        
    def _add_default_cond(self):
        one_query_cond = self._get_def_cond()
        self.add_condition(one_query_cond, 1)

    def reset(self):
        super().reset()
        self._add_default_cond()


class obj_list_IF:
    '''
    interface of obj_list
    '''
    
    version   = '1.0'
    sql_fromx = ''
    table_acc_mx = None
    
    def set_vars(self, table):
        self.table = table
        
    def set_acc_mx(self, table_acc_mx):
        # obj_role_rig_STRUCT
        self.table_acc_mx = table_acc_mx
    
    def _run_features( self, sql_from ):
        # do NOT overwrite !
        self.sql_fromx = 'from ' + sql_from
    
    def func_col2det(self, col_list):
        '''
        transform column list to DETAIL list of {}
        '''
        return [ {'id':col}  for col in col_list ]
    
    def func_cols_allow(self):  
        # get list of allowed column names
        
        col_det_list = self.get_col_fix()
        out=[]
        for row in col_det_list:
            out.append(row['id'])
        return out
    
    def get_main_config(self):
        """
        'tool.allow': [1] : set to -1 to DENY access to the OBJECT-type
        'acc.see.all': 0,1
        'use_table': e.g. 'EXP_SRES_V' #  A view
        'obj.table': use this table for SINGLE object links from the list view, e.g. whene table=EXP_SRES_V, 'obj.table'='EXP'
        'NEW.allow': 0,1    # allow NEW-button ?
        'NEW.roles': [ oROLE.BASE_ROLE.PM ]  # allow NEW for specific roles
        'chart.show' : 1
        'func.buts': list of function buttons ???
        """
        return {}
    
    def sec_table_lib(self, use_table):
        # can be replaced!
        return Sec_table_sql(use_table)
    
    def mod_menu(self, menu):
        pass
    
    def get_col_fix(self):
        '''
        get column list of {
            'id':, 
            'show': [1], -1
            'filt':  0,1  # show in search filter
            
        }
        '''
        result = []
        return result
    
    def get_xcols(self):
        """
        get extra columns
        """
        result = []
        return result
    
    def col_def(self, col):
        result = {}
        return result        
    
    def one_data_col(self, db_obj, col, pk_val, row_data_dict=None):
        pass    
    
    def get_one_query_dict(self, db_obj, one_query_dict):
        """
        create a new QUERY fictionary, which fits to the question
        outout: one_query_cond_STRUCT
        'col'
        'val'
        'op'
        """

        return one_query_dict
    
    def chart(self, db_obj, massdata):
        # build chart
        pass
    
#    
# --- helper methods ---
#
def menu_get_index(menu, key):
    '''
    needed when use mod_menu()
    '''
    mem_index = -1
    ind=0
    for row in menu:
        if row['m_name']== key:
            mem_index = ind   
            break
        ind = ind + 1  
    return mem_index