# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
list actions :  e.g. add role
File:           oDB_USER/list_act.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import sys
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.tab_abs_sql import Table_sql

from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib import oROLE




                
class plug_XPL(gPlugin) :  
    '''
     * @package list_act.py
     * @author  Steffen Kube (steffen@blink-dx.com)
     :var self._req_data:
       't' : table     
       'action':
         'add_role'  argu['role_key']
       argu:
         'role_key'  
    '''
    
    action=''

    

    def register(self):
        
        self.table = 'DB_USER'
        action = self._req_data.get( 'action' , '' )
        self.action = action
   
        self.tablib = table_cls(self.table)
        table_nice  = self.tablib.nice_name()
            

        self.infoarr['title']	  = 'List action of ' + table_nice
       
        self.infoarr['layout']    = 'ADM/user_list_act'
        self.infoarr['objtype']   = self.table
        self.infoarr['viewtype']  = 'list'
        self.infoarr['role.need'] = ['admin'] # allowed for content-admin
        self.infoarr['list.check_sel'] = 1
        self.infoarr['locrow']    = [
            {'url': 'ADM/home', 'text': 'Home'},
        ]

  
    def add_role(self, db_obj, db_obj2, argu):
        """
        add role to list of users
        """
        
        #table = self.table
        sql_from_order = self.sql_from_order
        
        role_key = argu.get('role_key', '')
                
        if role_key=='':
            self.setMessage('ERROR', 'No input "role_key" given.')
            return
     
        pk_col  = self.tablib.pk_col_get()
        sql_cmd = "x."+ pk_col +" from " + sql_from_order
        db_obj2.select_tuple(sql_cmd)  

        cnt=0
        infoarr=[]
        while db_obj2.ReadRow():
    
            user_id_loop  = db_obj2.RowData[0]
            
            try:  
                act_lib = oDB_USER.modify_obj(db_obj, user_id_loop)
                act_lib.add_role(db_obj, role_key) 
            except:
                message = str(sys.exc_info()[1])
                infoarr.append(['OBJ-ID:' + str(user_id_loop) + ' ADD_ROLE failed: ' + message])
            cnt = cnt + 1        
        
        if len(infoarr):
            self.setMessage( 'ERROR', str(len(infoarr)) + ' Problem(s) occurred.') 
            self._html.add_meta('error_list', infoarr )
            
        self.setMessage('OK', str(cnt) + ' Elements modified.') 
         
         
    def startMain(self) :
        
        db_obj  = self._db_obj1
        db_obj2 = self.db_obj2()
    
       
        table = self.table
        
        sql_select_lib = Table_sql(table)
        
        self.data_out = {}

        
        self.sql_from       = sql_select_lib.get_sql_from(db_obj)
        self.sql_from_order = sql_select_lib.get_sql_from_order(db_obj)
        #sql_nice = sql_select_lib.get_sql_nice()
        
        debug.printx( __name__, 'SQL: ' + self.sql_from )
        
        pk_col = self.tablib.pk_col_get()
        sql_cmd = "count(1) from " + self.sql_from
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        objcnt  = db_obj.RowData[0]        

        action = self._req_data.get( 'action' , '' )
        debug.printx( __name__, 'ACTION: ' + action )
        
        while 1:

            if action == 'add_role':
                
                roles = oROLE.Table.get_all_roles_nice(db_obj)
                role_list = []
                for row in roles:
                    one_row = (row['KEY'], row['NAME'])
                    role_list.append(one_row)                
                
                if int(self._req_data.get('go', 0)) < 1:
                    
                    self.data_out['form'] = {
                        'init': {
                            'title': 'Add a role to ' + str(objcnt) + ' users?',
                            'submit.text': 'Set',
                            'editmode': 'edit',
                            'app.space.prefix': 'ADM/'
                        },
                        'hidden': {
                            "mod"   : self._mod,
                            "action": 'add_role',
                            "go"    : 1,

                        },
                        'main': [ 
                            {
                            'object': 'select',
                            'name': 'argu[role_key]',
                            'edit': 1,
                            'inits': role_list,
                            'id': 1,  
                            }
                        ]
                    }
                    break                
                
                self.add_role(db_obj, db_obj2, self._req_data.get('argu', {}))
                
                break  
            
            self.setMessage('WARN', 'Action "'+action+'" unknown.')  
            
            break  # main loop break  
        
    
    def mainframe(self):
        
        db_obj  = self._db_obj1
        self.sh_main_layout(massdata=self.data_out)  