# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
update
File:           oCCT_TABLE/upd.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import sys

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.obj_mod import Obj_assoc_mod


class plug_XPL(gPlugin) :  
    '''
     * actions
     :param: id: TABLE_NAME
     :param  y params
       ...
    '''

    def register(self) :
        
        # user_full  = self.infoarr['user.fullname']
        
            
        self.objid = self._req_data.get('id','')             

        self.infoarr['title']	= 'Update CCT_TABLE'
        
        self.infoarr['layout']	= 'ADM/blank'        
        self.infoarr['id']	= self.objid
        self.infoarr['objtype'] = 'CCT_TABLE'
        self.infoarr['viewtype'] = 'object'
              
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]          
        
  
    def startMain(self) :
        
        db_obj = self._db_obj1

        if 'y' not in self._req_data:
            self.setMessage('ERROR', 'Input data needed.')   
            return
        
        tablename='CCT_COLUMN'
        mod_lib = Obj_assoc_mod(db_obj, tablename, self.objid)
        
        parx = self._req_data['y']
        for main_col, main_row in parx.items():
            
            args={}
            for cct_col, value in main_row.items():
                args[cct_col]=value.strip()
            
            idarr={'COLUMN_NAME':main_col}
            mod_lib.update(db_obj, idarr, args)
            

        self._req_data_new = {
            'mod': 'ADM/obj_one',
            't':   'CCT_TABLE',
            'id':  str(self.objid)
            }
        self._forward = 1          
                
        
    def mainframe(self):

        self.sh_main_layout()    
