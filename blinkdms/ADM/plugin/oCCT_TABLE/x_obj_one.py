# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
extension for ../obj_one.py
File:           CCT_TABLE/obj_one.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.obj_one_IF import obj_one_IF
from blinkdms.code.lib.main_imports import *


class extend_obj(obj_one_IF):
  
                        
    def page_bottom(self, db_obj, db_obj2, massdata):
        """
        
        """
        target_table = self.objid
        
        self._html.add_meta('bot.include',1)  
        
        # get all columns
        table_lib = table_cls('CCT_COLUMN')
        
        sql_cmd = "* from CCT_COLUMN where TABLE_NAME=" + db_obj.addQuotes( self.table )
        db_obj.select_dict(sql_cmd)
        
        
        db_obj.ReadRow()     
        onerow = db_obj.RowData
        
        col_types=[]
        cols_head=[]
        for key,val in onerow.items():
            if key!='TABLE_NAME':
                cols_head.append(key)
                data_type_dict = table_lib.col_def2(key)
                
                # debug.printx( __name__, ':data_type_dict:'+key+':'+str(data_type_dict) )
                col_types.append(data_type_dict.get('dtype_t','STRING'))
       
        
        
        col_data=[]  
        
        '''
        ... struct ...
        'dtypes': data types
        'data': [
          [x,c,v]
        ]
        '''        
        col_tab_struct = {
            'header': {
                'title':'Columns'
            },
            'cols':cols_head,
            'dtypes':col_types,
            'data':col_data   
            
        }   
        sql_cmd = ','.join(cols_head) + " from CCT_COLUMN where TABLE_NAME=" + db_obj.addQuotes( target_table )+' order by POS'
        db_obj.select_tuple(sql_cmd)        
        while db_obj.ReadRow():    
            col_data.append(db_obj.RowData)   
            
        
        debug.printx( __name__, ':col_tab_struct Start'+str(col_tab_struct) )
        
        self._html.add_meta('bot_columns', col_tab_struct)