'''
SQL terminal plugin
'''
from blinkapp.code.lib.main_imports import *
from blinkapp.code.lib.app_plugin import gPlugin
import sys

class plug_XPL(gPlugin) :  
    '''
     * ROOT plugin: all tables
     * @package tab_all.inc
     * @author  Steffen Kube (steffen@blink-dx.com)
    '''

    def register(self) :

        self.infoarr['title']	= 'All tables'
       
        self.infoarr['layout']	= 'ADM/list_COMMON'      
        
        self.infoarr['locrow']  = [ {'url':'ADM/home', 'text':'Home'} ]


    def startMain(self) :
        pass
        
    def mainframe(self):
        
        db_obj  = self._db_obj1
        
        dbid    = session['sesssec']['dbid'] 
        db_user = session['sesssec']['dbacc']['user']
        schema = db_user + '_tab'
        
        columns = ['Col-Defs', 'Content', 'NICE_NAME', 'TABLE_TYPE', 'CCT_TABLE_NAME']
        
        sql_cmd = "TABLE_NAME from information_schema.tables where TABLE_SCHEMA ='"+schema+"' order by TABLE_NAME"
        db_obj.select_tuple(sql_cmd)
        all_data = []
        while db_obj.ReadRow():
            tab_loop   = db_obj.RowData[0]   
            tab_loop_u = tab_loop.upper()
            
            cct_table_cont={}
            cct_table_cont_tmp = session['db_cache']['tables'].get(tab_loop_u,None)
            if cct_table_cont_tmp:
                cct_table_cont = cct_table_cont_tmp['feats']
            
            tab_html    = '<a href="?mod=ADM/obj_one&t=CCT_TABLE&id='+tab_loop_u+'">'+tab_loop+'</a>'
            tab_content = '<a href="?mod=ADM/obj_list&t='+tab_loop_u+'">Content</a>'
            data_row=[tab_html, tab_content, cct_table_cont.get('TABLE_TYPE',''), cct_table_cont.get('NICE_NAME',''), 
                      cct_table_cont.get('CCT_TABLE_NAME','') ]
            all_data.append(data_row)        
             
        massdatax={'data':all_data, 'title':'All tables from schema: '+ schema, 'opt': {'safe':1 }, 'cols': columns }
        self.sh_main_layout( massdata=massdatax )  
