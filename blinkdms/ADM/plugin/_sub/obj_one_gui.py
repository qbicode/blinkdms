# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
GUI methods for one_obj
File:           obj_one_gui.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *

class Mainobj:
    
    def __init__(self, table, objid):
        self.table =table 
        self.objid =objid
        debug.printx( __name__, 'table1: ' + str(self.table) ) 
        
    def get_nav(self, active_tab=''):
        
        table_lib = table_cls(self.table)
        
        url_adder = '&t=' + self.table +'&id='+str(self.objid)
        base_url = '?mod=ADM/obj_one'  + url_adder
        meta_url = '?mod=ADM/obj_meta' + url_adder   
        
        debug.printx( __name__, 'table2: ' + str(self.table) ) 
        debug.printx( __name__, 'url_adder: ' + str(url_adder) ) 
        
        nav = [
              {'title':'Main',    'id':'main', 'url': base_url +'&tab=main'},
              {'title':'Meta',    'id':'meta', 'url': meta_url +'&tab=meta'},
            ]
        
        if len(table_lib.pk_cols())==1:
            nav.append( {'title':'Vario columns', 'id':'vario', 'url': meta_url +'&tab=vario'} )
            nav.append( {'title':'Mod Log', 'id':'mod_log',     'url': meta_url +'&tab=mod_log'} )
               
        nav.append( {'title':'Table Description', 'id':'tab.descr', 'url': meta_url +'&tab=tab.descr'} )
             
        i=0
        for row in nav:
            if row['id']==active_tab: nav[i]['active']=1
            i=i+1
        
        return nav