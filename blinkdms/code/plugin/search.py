# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
search
File:           search.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
import sys

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oDOC import oDOC_VERS
from blinkdms.code.lib.tab_abs_sql import Table_sql



class plug_XPL(gPlugin) :  
    '''
     :var self._req_data:
      REQUIRED

       'text': arguments
    OPTIONAL:
    
    ''' 
  
    obj_ext_lib  = None # extender class

    def register(self) :

        self.infoarr['title']	 = 'Search'
        self.infoarr['layout']	 = 'empty'
        self.infoarr['viewtype'] = 'tool'
        
  
        
    def startMain(self):
        
        db_obj = self._db_obj1
        
        if 1:
            
            
            session['sessvars']['head.search'] = {'text': self._req_data['text'] }

            text = self._req_data['text'].strip()
            
            context = session['sesssec']['my.context'] 
            tablib = oDOC_VERS.Table(context)
            full_query_cond = tablib.search_cond_EDIT(text)
            use_table = tablib.table
            
            sql_build_lib = Table_sql(use_table)
            sql_build_lib.reset()
            sql_build_lib.add_condition_full(full_query_cond)
            
            sql_from = sql_build_lib.get_sql_from(db_obj)

            sql_cmd = "count(x.VERSION_ID) from " + sql_from
            db_obj.select_tuple(sql_cmd)
            db_obj.ReadRow()
            objcnt_sel = db_obj.RowData[0]

                     
            
            if objcnt_sel==1:
                
                # forward to the single document
                
                sql_cmd = "x.VERSION_ID from " + sql_from
                db_obj.select_tuple(sql_cmd)
                db_obj.ReadRow()
                v_id = db_obj.RowData[0]                
                
                doc_link = 'doc_view'
                if context=='EDIT':
                    doc_link = 'doc_edit'
                    
                req_data = {
                    'mod': doc_link,
                    'id': str(v_id)
                }                
            
            else:
                
                sql_build_lib.save_session()  # save QUERY in session
            
                # do an interrnal forward to plugin "obj_list" which is showing the search
                req_data = {
                    'mod': 'doc_list',
                }               

            
            self._req_data_new = req_data
            self._forward = 1
    
    def mainframe(self):

        self.sh_main_layout()    
    
 
        
        