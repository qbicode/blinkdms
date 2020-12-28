# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
- a TABLE can have an extension-file: {app.type}/o{TABLE}/x_obj_list.py
File:           table_out.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import math

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.gui.obj_list_sub import Obj_list_sub
from blinkdms.code.lib import f_module_helper
from blinkdms.code.lib.obj_list_IF import obj_list_IF

class table_show:
    """
    show a pure table of an OBJECT type
    OUTPUT: self.list_struct
    
    """
    
    column_struct = None
    """
    :var column_struct: see obj_list_sub.py : column_out_STRUCT
    """
    
    list_struct = {} 
    """
    :var list_struct_STRUCT
    'columns' : only needed when build_column_struct() is called
    'header': list of dict obj_list_sub.py:"column_STRUCT" { 
       'name':col, 
       'nice':col_nice, 
       'show': 0,1 : some columns will not be shown, if not selected in preferences ..
       ...
       }
    'data': list of list of data
       order: index1: by row of select
       order: index2 (one row): ordered by 'header'-order
    'meta':
      'pk_col_ind' : column index of pkcol in 'data' rows
      'imp_col_ind':  column index of  most important col
      
    'cnt_per_page' : 0 : all  
    'page_no' : starts with 1
    """
    
    tab_order_list = [] #  [ {'col':column, 'ord': 'ASC|DESC'} ]
    _meta = {}
    
    def __init__(self, table, list_struct, tab_order_list, admin_area=0):
        '''
        :param list_struct: list_struct_STRUCT : this is the OUTPUT !
        '''
        self._meta = {}
        self.column_struct = None
        self.table = table
        self.list_struct    = list_struct
        self.tab_order_list = tab_order_list
        self.list_helper = Obj_list_sub(self.table, admin_area)
        
        self.obj_ext_lib = None
        # check for OBJECT specific library in PLUGIN
        
        module     = None
        my_context = session['sesssec'].get('my.context','')
        if my_context=='SERVICE':
            # try to load SERVICE extension
            module_path_s = session['globals']['gui.root_dir'] + '/plugin/s/o'+ table +'/' + 'x_obj_list'
            module = f_module_helper.check_module(module_path_s, 1)  
            
        if module is None:      
        
            path_use = session['globals']['gui.root_dir'] + '/plugin/o'+ table +'/x_obj_list'
            absolute_path_flag = 1
            if admin_area:
                path_use =  'plugin/ADM/o'+ table +'/x_obj_list'
                absolute_path_flag = 0        
            module = f_module_helper.check_module( path_use, absolute_path_flag)
            
        if module is not None:
            self.obj_ext_lib = module.extend_obj()        
        else:
            self.obj_ext_lib = obj_list_IF()          
    
    def get_meta(self):
        return self._meta
    
    def build_column_struct(self, db_obj):
        """
        input: self.list_struct['columns']
        create self.column_struct
        """
        if 'columns' not in self.list_struct:
            raise BlinkError (1, 'No columns given.')
        
        if not len(self.list_struct['columns']):
            raise BlinkError (2, 'No columns given.')        
        
        # ----------------
        # table header
        
        columns_show  = self.list_struct['columns']  
        column_struct = self.list_helper.column_struct_get(db_obj, columns_show, self.tab_order_list) 
        self.column_struct = column_struct
    
    def set_col_feature(self, col_xcode, key, val):
        # set one feature of a column
        
        for i,row in enumerate(self.column_struct['show_cols']):
            if row['name']==col_xcode:
                self.column_struct['show_cols'][i][key]=val
                break
        
    def build_header(self):
        '''
        build the header
        '''
        
        if self.column_struct == None:
            raise BlinkError(1, 'Input missing: self.column_struct .')
        
        self.list_struct['header'] = self.column_struct['show_cols'] 
        self.list_struct['meta']   = self.column_struct['meta']        
        
    
    def build_data(self, db_obj, db_obj2, sql_from_order, options={} ):
        """
        - SHOW table WITHOUT build_column_struct()
        need input: self.column_struct
        produce for HTML-table: header + body 
        
        IN:
          self.list_struct[]
            'page_no'
            'cnt_per_page' : 0 : all
        OUT: self.list_struct
            ['data']   !!!!!!!!!
            ['meta']['modal_id']
            ['meta']['select.type']
        :param list columns: show these columns
        :param options: dict 
          'modal_info' : {'id':..}
          'sql.exec.deny' : 0,1 => DENY execution, use this method just to produce outer structure

        """

        if 'header' not in self.list_struct == None:
            raise BlinkError(1, 'Input missing: self.list_struct[header] .')
        
        
        column_header = self.column_struct['show_cols']
        
        # debug.printx( __name__, 'column_header:' + str(column_header ) )

        modal_info = options.get('modal_info', None)
        select_type='checkbox'
        if modal_info is not None:
            select_type='select'
            self.list_struct['meta']['modal_id'] = modal_info['id']
        self.list_struct['meta']['select.type']= select_type       
        
        cols_select  = self.column_struct['sel_cols']
        pk_col_index = self.column_struct['meta']['pk_col_ind']

    
        if options.get('sql.exec.deny',0):
            return # stop EXECUTION !
    
        """
        select the data ...
        """
        cnt_per_page = self.list_struct['cnt_per_page']

        
        sql_cmd = ", ".join(cols_select) + ' ' + sql_from_order
        db_obj2.select_tuple(sql_cmd)
        
        # may be: match query_cols to columns_show: because: MORE columns are queried than columns_show
        # query_cols = db_obj.column_names() 
        
        all_data = []
        self.list_struct['data'] = all_data # list of list of values 
        


        if cnt_per_page > 0:

            page_now = self.list_struct['page_no']
            page_max = math.ceil( self.list_struct['objcnt_sel'] / cnt_per_page )
            
            self._meta['page.no'] = page_now
            self._meta['page.max']=page_max 
            
            page_prev = page_now-1 if (page_now-1 >=1) else 0
            page_next = page_now+1 if (page_now+1 <= page_max) else 0
            
            prev_str = str(page_prev) if page_prev else ''
            next_str = str(page_next) if page_next else ''
            
            self._meta['page.prev']= page_prev 
            self._meta['page.next']= page_next 
            self._meta['page.min1']= prev_str 
            self._meta['page.plus1']= next_str        
        else:
            page_now = 1
        
        
        do_show =0
        loop_cnt=0
        show_cnt=0
        page_cnt=1
        if page_now<=1:
            do_show =1
        show_start_cnt = (page_now-1) * cnt_per_page
        
        obj_lib_cache={}
        for row in column_header:
            if 'fk_t' in row:
                fk_table = row['fk_t']
                fk_obj_lib = obj_abs(fk_table, 0)
                obj_lib_cache[fk_table] = fk_obj_lib
                
        # debug.printx( __name__, 'obj_lib_cache: ' + str(obj_lib_cache) )           
        
        
        while db_obj2.ReadRow():
            
            if show_cnt > cnt_per_page and cnt_per_page:
                break
            
            if loop_cnt>=show_start_cnt:
                do_show = 1
        
            if do_show:   
                 
                row_data = list(db_obj2.RowData) 
                row_out = [] # or do this : [None]*len(column_header) # create filled list
                # prepare data
                
                sql_index = 0
                for head_row in column_header:
                    
                    val = None
                    
                    if head_row['sqlsel']: # only ignore NON-SQL columns ; e.g. "y.countit"
                    
                          
                        val = row_data[sql_index]
                        
                        if val is not None:
                            
                            if head_row.get('d_type',0)==4:
                                val = '***' # do not show passwords
    
                            if 'fk_t' in head_row:
                                #
                                # get foreign object
                                #
                                 
                                fk_table    = head_row['fk_t']
                                obj_lib_cache[fk_table].set_objid(val)
                                val_new     = obj_lib_cache[fk_table].obj_nice_name(db_obj)
                                val = val_new
                        
                        
                                
                        sql_index = sql_index + 1 
                        
                    row_out.append(val)
                            

               
                #
                # get special data ...
                #
                if self.obj_ext_lib is not None:
                    
                    pk_val = row_out[pk_col_index]
                    # debug.printx( __name__, 'row_out_EXO: i:' + str(pk_col_index) + " val:"+str(pk_val) )  
                    offset  = len(row_out)
                    
                    # transform SQL-answer LIST into DICT
                    sql_index = 0
                    row_data_dict={} # KEY, VALUE dict
                    for head_row in column_header:
                        if head_row['sqlsel']: # only ignore NON-SQL columns ; e.g. "y.countit"
                            val = row_data[sql_index]
                            row_data_dict[head_row['name']] = val
                            sql_index = sql_index + 1 
                    
                    data_ind = 0
                    for row in column_header:
                        col_xcode = row['name']
                        col_prefix = col_xcode[0] 
                        col        = col_xcode[2:] 
                        
                        if col_prefix=='y':
                            value = self.obj_ext_lib.one_data_col(db_obj, col, pk_val, row_data_dict)
                            row_out[data_ind] = value
                            
                        data_ind = data_ind + 1    
                        
                
                # debug.printx( __name__, 'row_out2: ' + str(row_out) )               
                
                all_data.append(row_out)  
                show_cnt = show_cnt + 1
                
                
            loop_cnt = loop_cnt + 1
            
    def show(self, db_obj, db_obj2, sql_from_order, options={} ):
        """
        short cut show
        """
        self.build_column_struct(db_obj)
        self.build_header()
        self.build_data(db_obj, db_obj2, sql_from_order, options )