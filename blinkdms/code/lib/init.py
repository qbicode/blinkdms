# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"


"""
init vars
- manage session['db_cache']
    ['tables'] - table description
    ['t_data']   - some cached content of tables
       'APP_DATA_TYPE' : ID => {'name': , 'type':   }

File:           init.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from .debug import debug

class initvars_cls:
    """
    session['db_cache']['tables']
       TABLENAME : { 'feats': {},  'cols': {} }
    """
    
    def __init__(self, session_obj):
        self.session_obj = session_obj
    
    def tables(self, db_obj):
        
        tables = {}
        self.session_obj['db_cache']['tables'] = tables
        
        sql_cmd = "* from cct_table order by table_name"
        db_obj.select_dict(sql_cmd)
        
        
        while db_obj.ReadRow():
            table_loop = db_obj.RowData['TABLE_NAME']
            feats = db_obj.RowData
            feats['PRIM_KEYS']    = []
            feats['MOST_IMP_COL'] = ''
            tables[table_loop]    = {'feats': feats }
            
    def columns(self, db_obj):
        
        tables = self.session_obj['db_cache']['tables'] 
        
        sql_cmd = "* from cct_column order by table_name, pos"
        db_obj.select_dict(sql_cmd)
        
        while db_obj.ReadRow():
            
            data_loop = db_obj.RowData
            
            col_loop   = data_loop['COLUMN_NAME']
            table_loop = data_loop['TABLE_NAME']
            if data_loop['NICE_NAME']=='' or data_loop['NICE_NAME'] is None:
                
                if  data_loop['CCT_TABLE_NAME']!='' and data_loop['CCT_TABLE_NAME'] is not None:
                    # if links to foreign table : get nice name of foreign table
                    tmp_fk_feats = tables[data_loop['CCT_TABLE_NAME']]
                    data_loop['NICE_NAME'] = tmp_fk_feats['feats'].get('NICE_NAME','???')
                else:
                    data_loop['NICE_NAME'] = col_loop.lower()
            
            if table_loop in tables:
                if 'cols' not in tables[table_loop]:
                    tables[table_loop]['cols'] = {}
                
                if col_loop=='CCT_ACCESS_ID' or col_loop=='EXTRA_OBJ_ID':
                    data_loop['EDITABLE'] = 0
                    data_loop['VISIBLE']  = 0
                if data_loop['PRIMARY_KEY']>0:
                    data_loop['EDITABLE'] = 0
                    tables[table_loop]['feats']['PRIM_KEYS'].append(col_loop)
                    
                if data_loop['MOST_IMP_COL']>0:
                    tables[table_loop]['feats']['MOST_IMP_COL'] = col_loop  
                    
                tables[table_loop]['cols'][col_loop] = data_loop
                
    def table_content(self, db_obj):
        '''
        manage ['t_data']
        '''
        
        self.session_obj['db_cache']['t_data'] = {}

        # APP_DATA_TYPE
        # DEPRECATED:  self.session_obj['db_cache']['t_data']['APP_DATA_TYPE'] = data_vals

    
    def init_all(self, db_obj):
        
        self.tables(db_obj)
        self.columns(db_obj)
        self.table_content(db_obj)
        
        #debug.printx(__name__, '(95):session_obj[db_cache]:' + str(self.session_obj['db_cache']))
        