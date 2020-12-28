# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
SINGLE object : META view 
- look for extension-file: {TABLE}/obj_one.py
File:           obj_meta.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
import sys
import importlib

from blinkapp.code.lib.main_imports import *
from blinkapp.code.lib.app_plugin import gPlugin
from blinkapp.code.lib.obj_mod_meta import obj_mod_meta
from blinkapp.code.lib import f_module_helper




class plug_XPL(gPlugin) :  
    '''
     :var self._req_data:
      REQUIRED
       't'  : table 
       'id' : ID of object
     
    '''
    
  
    obj_ext_lib  = None # extender class
    table = ''
    objid = 0

    def register(self) :
        
        self.table = self._req_data.get('t','')
        nice =''
        if  self.table!='':
            table_lib = table_cls(self.table)
            nice = table_lib.nice_name()

        self.infoarr['title']	= 'Table description'
        self.infoarr['html']	 = 'ADM/home'
        self.infoarr['layout']	 = 'ADM/tab_desc'
        self.infoarr['viewtype'] = 'tool'
        self.infoarr['objtype'] = self.table
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
            {'url':'ADM/obj_list&t='+self.table, 'text': 'List of '+nice },
        ]         


    def startMain(self) :
        
        db_obj = self._db_obj1

        table_lib = table_cls('CCT_COLUMN')
        cols = table_lib.get_cols()
        
        self.dataout = {}
        
        sel_option={ 'order': 'POS' }
        db_obj.select_col_vals( 'CCT_COLUMN', {'TABLE_NAME': self.table}, cols, sel_option )
        dataout_cols=[]
        dataout_cols.append(cols) # header
        
        debug.printx( __name__, '1:'+ str(cols)  )
        
        while db_obj.ReadRow():
            out_row = []     
            for col_def in cols:
                val = db_obj.RowData[col_def] 
                out_row.append(val)
            dataout_cols.append(out_row)        

        debug.printx( __name__, '2:'+ str(dataout_cols)  )
        self.dataout['tab.descr'] = dataout_cols

    
    def mainframe(self):
        
        db_obj = self._db_obj1


        self.sh_main_layout( massdata=self.dataout)    
        
   