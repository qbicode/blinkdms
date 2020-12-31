# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
support FORM building
File:           obj_one_sub.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.obj.obj_info import Obj_info_lev2

class Mainobj:
    '''
    :vardef col_list_seriell_STRUCT:  list of column definitons for a form [
    
        {'col': 'x.COLNAME' => COL_XCODE: STANDARD COLUMN
         'val': OPTIONAL
         }
        {'col': 'y.COLNAME',   => EXTRA COLUMN
         'col.nice':
         'edit': 0,1
         'type': 'text', 'select'
         'inits': init array e.g. for 'select'
         'val':
         'val.nice'
         'multiple' : 0,1 => for SELECT
         'fk_t': foreign table
         'required' : 0,1
         'notes' : [OPT]
        }
        
    ]
    
    :vardef form_seriell_STRUCT:  html-form structure {
        'main' : col_list_seriell_STRUCT,
        'form' : { 
           'init': {
             'submit.text': ''
            
           }
        }
    }
    
    '''
    
    objlib   = None
    data_out = {} # format: form_seriell_STRUCT

    def __init__(self, table, objid):
        # debug.printx(__name__, "START_bottom")
        self.table = table
        self.objid = objid
        self.objlib = obj_abs(table, objid) 
        self.table_lib = table_cls(table)
        self.data_out = {}
        
        self._is_admin = GlobMethods.is_admin()
        
    @staticmethod
    def colums_2xcode(columns):
        xcodes=[]
        for col in columns:
            xcodes.append( {'col':'x.'+col} )
        return xcodes 
    
    @staticmethod
    def col_xcode_split(col_xcode):
        '''
        return (PREFIX, COLUMN_RAW) e.g. ('x','NAME')
        '''
        
        if col_xcode[1:2]!='.':
            raise BlinkError(1, 'col_xcode "'+col_xcode+'" has invalid format.')
        prefix  = col_xcode[0:1]
        col_raw = col_xcode[2:]
        return (prefix,col_raw)         

    def features(self, db_obj):
        
        obj_lib_lev2 = Obj_info_lev2( self.table, self.objid )
        return obj_lib_lev2.features(db_obj)

    def form_data(self, db_obj, obj_features, editmode_sum):
        """
        create standard form data
        - DIFFERENCE to form_data2(): INPUT: obj_features
        - show all columns of obj_features['vals'] which are ALLOWED
        - show columns of obj_features['xtra'] : so called 'y.' columns ...
        :param obj_features: obj_info.py: objFeatStruct
        :param editmode_sum: int : 0,1
        :return dict: data_out
        """
        
        columns_show = self.table_lib.get_cols_allow()
        
     
        main_feat_out = []
        self.data_out = {
            'main' : main_feat_out,
            'form' : 
                 { 'init': {} }
        }
        
        edit_allow_all = editmode_sum
        
        id_cnt=1
        
        for col, val in obj_features['vals'].items():  # columns_show:
            
            # val     = obj_features['vals'][col]
            if col not in columns_show:
                continue
            
            col_def = self.table_lib.col_def2(col)
            
            if val == None:
                val_out = ''
            else: val_out = val
                
            editallow = 1 if (col_def['EDITABLE']>0 and edit_allow_all) else 0
            if col_def['APP_DATA_TYPE'] == 'PASSWORD':
                if val_out!='':
                    val_out   = '***'
                editallow = 0
            
            one_row = {
                'col':col,
                'col.nice':col_def['NICE_NAME'],
                'val' : val_out,
                'edit': editallow,
                'type': 'text'
            }
            
            if col_def.get('dtype_n','')=='notes':
                one_row['type'] = 'textarea'
            
            
            if col_def['CCT_TABLE_NAME'] is not None:
                one_row['fk_t'] = col_def['CCT_TABLE_NAME']
                one_row['id']   = id_cnt
                one_row['type'] = 'objlink'
                if val is not None:
                    tmp_obj_lib  = obj_abs( one_row['fk_t'], val)
                    tmp_obj_nice = tmp_obj_lib.obj_nice_name(db_obj)
                else: tmp_obj_nice=''
                one_row['val.nice']   = tmp_obj_nice
                
                id_cnt = id_cnt + 1
            
            main_feat_out.append( one_row )
            
         
        return self.data_out
    
    def form_data2(self, db_obj, col_list, editmode_sum):
        """
        create standard form data
        - DIFFERENCE to form_data(): INPUT: col_list
        - the INPUT features col_list OVERWRITES the table-definition col_def
        
        :param col_list:  col_list_seriell_STRUCT  
        :param editmode_sum: int : 0,1 
        :return dict:     form_seriell_STRUCT
        """
        
        columns_show = self.table_lib.get_cols_allow()
        
      
        
        main_feat_out = []
        self.data_out = {
            'main' : main_feat_out,
            'form' : 
                 { 'init': {} }
        }
        
        edit_allow_all = editmode_sum
        
        id_cnt=1
        
        for col_row in col_list:  
            
            # col, val
            col_XCODE = col_row['col']
            val = col_row.get('val', None)

            if col_XCODE[1]!='.': 
                raise BlinkError(1, 'internal parameter error: DOT expected in column-name')
            
            if val == None:
                val_out = ''
            else: val_out = val
               
            if col_XCODE[0:2]=='x.': 
                
                col = col_XCODE[2:]
                if col not in columns_show:
                    continue                
                
                col_def = self.table_lib.col_def(col)
                
                
                editallow = 0
                if edit_allow_all:
                    
                    if 'EDITABLE' in col_row:
                        editallow = col_row['EDITABLE']
                    else:
                        if col_def['EDITABLE']>0: editallow = col_def['EDITABLE']
                        
                    if editallow==2 and not self._is_admin:
                        # if editallow=2: only ROOT or SU_FLAG=1 can edit ...
                        editallow = 0
                    
                    
                if col_def['APP_DATA_TYPE'] == 'PASSWORD':
                    if val_out!='':
                        val_out   = '***'
                    editallow = 0
                
                one_row = {
                    'col':  col_XCODE,
                    'col.nice':col_def['NICE_NAME'],
                    'val' : val_out,
                    'edit': editallow,
                    'type': 'text',
                    'notes': col_def['NOTES'],
                }
                
                if col_def.get('NOT_NULL',0)> 0:
                    one_row['required'] = 1
                
                if col_def['CCT_TABLE_NAME'] is not None:
                    one_row['fk_t'] = col_def['CCT_TABLE_NAME']
                    one_row['id']   = id_cnt
                    one_row['type'] = 'objlink'
                    if val is not None:
                        tmp_obj_lib  = obj_abs( one_row['fk_t'], val)
                        tmp_obj_nice = tmp_obj_lib.obj_nice_name(db_obj)
                    else: tmp_obj_nice=''
                    one_row['val.nice']   = tmp_obj_nice
                    
                    id_cnt = id_cnt + 1
                    
            if col_XCODE[0:2]=='y.': 
                
                # EXTRA column
                editallow = 0
                if col_row['edit'] and edit_allow_all:
                    editallow = 1
                
                one_row = col_row.copy()
                
                one_row['val']  = val_out
                one_row['edit'] = editallow
            
            main_feat_out.append( one_row )
            
        
        
        return self.data_out
    
    def assoc_data(self, assoc_data):
        '''
        get assoc data
        [ {
        't' : assoc table
        'nice'
        'cnt'
        'action': {
          'url'
          'text'
        }
        ]
        '''
        
        output = []
        for row in assoc_data:
            table_loop_lib = table_cls(row['t'])
            nice = table_loop_lib.nice_name()
            
            row_new = row.copy()
            row_new['nice'] = nice
            output.append(row_new)
            
        return output
    
    def set_data(self, data_vals):
        """
        - set data 'val' for each allowed row to form
        :param fata_vals: { COL_XCODE : VAL }
        :return: sanitized values
        """
        
        if not len(self.data_out['main']):
            raise BlinkError (1, 'Form fields are not defined.')

        # set data vals
        i=0
        for row in self.data_out['main']:
            
            if row.get('edit',0) :
                # if EDIT allowed ...
                column = row["col"]
                val_in = data_vals.get(column,'').strip()
                self.data_out['main'][i]['val'] = val_in
            i = i + 1
        
    def get_form(self):
        return self.data_out