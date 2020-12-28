# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
basic helper methods for obj_list.py
- a TABLE can have an extension-file: /o{TABLE}/x_obj_list.py
File:           obj_list_sub.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>

Session-vars: 
  * session['user_glob']['obj_list.{TABLE}'] = { data }

:param dict column_out_STRUCT: STRUCT defintion
    'sel_cols' : tuple of selected columns
    'show_cols':  column_STRUCT []
      'name' : e.g. 'x.NAME'
      'nice' : nice name
      'show' : 0,1
      'notes': notes
      'sort' : sort flag 'DESC' or 'ASC'
      'sqlsel' : 0,1 is a SQL-select column ...
      'd_type' : data type = APP_DATA_TYPE_ID
      ### 'selid': index from SQL-query
      'fk_t':
      'fk_pk'
      ]
    'meta'
       'table'      :  table name
       'pk_col_ind' :  index in the header
       'imp_col_ind':  index in the header
"""

import json
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib import f_module_helper
from blinkdms.code.lib.obj_list_IF import obj_list_IF
from blinkdms.code.lib  import oUSER_PREF

class Obj_list_sub:
    
    user_prefs = {} 
    
    def __init__(self, table, admin_area=0):
        self.table = table
        self.table_lib = table_cls(self.table)
        
        self.pref_key = 'obj_list.' + self.table
        if not self.pref_key in session['user_glob']:
            session['user_glob'][self.pref_key] = {}
        self.user_prefs = session['user_glob'][self.pref_key]
                  
            
        # check for OBJECT specific library in PLUGIN
        module     = None
        my_context = session['sesssec'].get('my.context','')
       
            
        if module is None:  
            # other context
            path_use = session['globals']['gui.root_dir'] + '/plugin/o'+ table +'/x_obj_list'
            absolute_path_flag = 1
            if admin_area:
                path_use =  'plugin/ADM/o'+ table +'/obj_list'
                absolute_path_flag = 0
            module = f_module_helper.check_module( path_use, absolute_path_flag)
            
        
            
        if module is not None:
            self.obj_ext_lib = module.extend_obj()        
        else:
            self.obj_ext_lib = obj_list_IF()        
     
    def _store_user_prefs(self):
        session['user_glob'][self.pref_key] = self.user_prefs    
        
    def save_user_prefs_DB(self,db_obj):
        # save user prefs for TABLE list  in database
        user_lib = oUSER_PREF.MainLib()
        user_lib.save_one_key_val_cls(db_obj, self.pref_key, session['user_glob'][self.pref_key])
    
    def get_all_cols(self) :
        '''
        get ALL visible columns + CCT_ACCESS cols
        :return: list of columns (with x. and a.)
        '''
        col_out = []
        cols = self.table_lib.get_cols()
        
        for col in cols:
            
            show=1
            col_feat = self.table_lib.col_def(col)

           
            if not col_feat['VISIBLE']:
                show=0
                
            if show:
                col_out.append('x.'+col)
        
        # add extra columns
        xcols = self.obj_ext_lib.get_xcols()
        if len(xcols):
            for col in xcols:
                col_out.append('y.'+col)
                
        return col_out
        
     
        
    def set_sort_prefs(self, sort_prefs):
        '''
        :param sort_prefs: [ {'col':column, 'ord': 'ASC|DESC'} ]
        
        '''
        self.user_prefs['sort'] = sort_prefs
        self._store_user_prefs()   
        
    def get_sort_prefs(self):
        '''
        :param sort_prefs: [ {'col':column, 'ord': 'ASC|DESC'} ]
        
        '''
        if 'sort' not in self.user_prefs:
            # use PRIMARY KEY
            pk = self.table_lib.pk_col_get()
            sort_prefs = [{'col':'x.'+pk, 'ord':'DESC'}]
        else:
            sort_prefs = self.user_prefs['sort']
            
        return sort_prefs
    
    def get_col_fix(self):
        return self.obj_ext_lib.get_col_fix()
    
    def func_cols_allow(self):
        return self.obj_ext_lib.func_cols_allow()    
    
    def set_col_prefs(self, col_prefs):
        '''
        input: list of columns
        '''
        self.user_prefs['cols'] = col_prefs
        self._store_user_prefs()      
        
    def get_col_prefs(self):
        """
        
        get just the SHOWN columns, not the real selected ...
        
        return user preferred columns from self.session_obj['user_glob']['obj_list'] = 
            json(  {
               'cols': tuple of columns
                  } )
        :return: tuple of columns:  'x.NAME', 'a.DB_USER_ID', ... 
        """         
            
        if 'cols' not in self.user_prefs:
            
            col_prefs = []
            cols = self.table_lib.get_cols()
            
            for col in cols:
                show=1
                col_feat = self.table_lib.col_def(col)
                if col_feat['VISIBLE']<1:
                    show=0
                #if col_feat['MOST_IMP_COL']>0:
                #    show=1

                if show:
                    col_prefs.append('x.'+col)
            
        else:
            col_prefs  = self.user_prefs['cols']
        
        #debug.printx(__name__, "get_col_prefs::col_prefs:" + str(col_prefs))
            
        return col_prefs
    
    def filter_columns_get(self, db_obj, cols_show):
        """
        get structure for the SEARCH form
        :param cols_show: 
          'x.NAME'
          'y.special'
        
        :return: filter_cols_STRUCT
            'name' : e.g. 'x.NAME'
            'nice' : nice name
            ]
        """
        
        filter_cols=[]
        #table_lib_acc = table_cls('CCT_ACCESS')
        
        # build filter_cols struct ...
        for col_xcode in cols_show:
            
            # col_xcode : e.g. 'x.NAME'
            col_prefix = col_xcode[0] 
            col        = col_xcode[2:]
            
            if col_prefix=='x':
                col_def  = self.table_lib.col_def(col)
           
            elif col_prefix=='y':
                continue # ignore    
                
            col_nice  = col_def['NICE_NAME']
            
            show_row = { 
                'name':col_xcode, 
                'nice':col_nice, 
                } 

            filter_cols.append( show_row )
            
        return filter_cols
    
    def column_struct_get(self, db_obj, cols_show, tab_order_list):
        """
        transform [COLUMN-names] ==> column_out_STRUCT
        :param cols_show: tuple of columns: 'x.NAME', 'a.DB_USER_ID', ... 
        :param tab_order_list: []
        :return: column_out_STRUCT
        """
        
        std_cols = self.table_lib.get_cols()
        
        sel_cols = []
        show_cols= []        
        
        column_struct = {
         'meta': {
             'table': self.table
             },
         'sel_cols': sel_cols,
         'show_cols': show_cols
        }
        
        #table_lib_acc = table_cls('CCT_ACCESS')
        pk_col = self.table_lib.pk_col_get( )
        
        # collect standard select columns
    
        
        cols_not_show = []
        
        for col in std_cols:
            
            col_xcode = 'x.'+col
            select=0
            
            col_def  = self.table_lib.col_def(col)
            
            if col_def['PRIMARY_KEY']>0:
                select=1
                
            if select:
                # this column was part of the SELECT query
                if col_xcode not in cols_show:
                    cols_show.append(col_xcode)
                    cols_not_show.append(col_xcode)

        
        
        sql_index  = 0
        head_index = 0
        # debug.printx(__name__, "(262) cols_show:" + str(cols_show))
        
        # produce temporary DICT for order by info
        order_dict={}
        for row in tab_order_list:
            order_dict[row['col']] = row['ord']
        
        # build show_cols struct ...
        for col_xcode in cols_show:
            
            # col_xcode : e.g. 'x.NAME'
            col_prefix = col_xcode[0] 
            col        = col_xcode[2:]
            
            add_to_select = 1
            if col_prefix=='x':
                col_def  = self.table_lib.col_def(col)

            elif col_prefix=='y':
                
                col_def  =  self.obj_ext_lib.col_def(col)
                # debug.printx(__name__, "column_struct_get: y::" +  col + ' def: '+str(col_def) )
                
                add_to_select = 0 # special columns do not apear in SQL ..
            
            if not len(col_def):
                raise BlinkError(1, 'Column "'+ col_xcode +'" not defined in Meta-Def.')
                  
            if add_to_select:
                sel_cols.append(col_xcode)
                
            col_nice  = col_def['NICE_NAME']
            is_pk     = col_def.get('PRIMARY_KEY', 0)
            d_type = col_def.get('APP_DATA_TYPE', 0)
                    
            do_show = 1
            if col_xcode in cols_not_show:
                do_show = 0
            
            if do_show:
                show_row = { 
                    'name'  :col_xcode, 
                    'nice'  :col_nice, 
                    'notes' : col_def['NOTES'],
                    'show'  : do_show,
                    'sqlsel': add_to_select, 
                    'd_type': d_type
                    }
                if col_prefix == 'x':
                    show_row['sort.a'] = 1
                    
            else:
                show_row = { 
                    'name'  : col_xcode, 
                    'show'  : do_show,
                    'sqlsel': add_to_select, 
                    'd_type': d_type
                    }                
            
            if is_pk:
                show_row['pk'] = is_pk
            if col_prefix=='x' and col == pk_col:
                column_struct['meta']['pk_col_ind'] = head_index
            if col_prefix=='x' and col_def['MOST_IMP_COL']>0: # need "x" , otherwise conflict with "a" data
                column_struct['meta']['imp_col_ind'] = head_index    
            if col_xcode in order_dict:
                show_row['sort'] = order_dict[col_xcode] # DESC or ASC
            
            if ( col_def.get('CCT_TABLE_NAME',None) != None ) and do_show:
                
                fk_table = col_def['CCT_TABLE_NAME']
                tmp_table_lib = table_cls(fk_table)
                
                #debug.printx(__name__, "column_struct_get: fk_table:" +fk_table + " xcode:"+col_xcode+ " struct: "+ str(show_row) )
                
                fk_pk = tmp_table_lib.pk_col_get()
                
                show_row['fk_t']  = fk_table
                show_row['fk_pk'] = fk_pk
            
            if add_to_select:  
                sql_index = sql_index + 1            
            
            show_cols.append( show_row )
            
            head_index = head_index + 1
            

        # debug.printx(__name__, "(339) column_struct_get:column_struct:" + str(column_struct))
                
        return column_struct