# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
list actions : change owner
File:           list_act.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import sys
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.tab_abs_sql import Table_sql
#from blinkdms.code.lib.f_clip import clipboard
#from blinkdms.code.lib.obj_mod_meta import obj_mod_meta

#from blinkdms.code.lib.gui.obj_list_sub import Obj_list_sub
#from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.oDOC import oDOC



                
class plug_XPL(gPlugin) :  
    '''
     * @package folder.py
     * @author  Steffen Kube (steffen@blink-dx.com)
     :var self._req_data:
       't' : table     
       'action':
         'chown'  argu['user_id']
       argu:
         'user_id'  
    '''
    
    action=''

    

    def register(self):
        
        self.table = 'DOC'
        action = self._req_data.get( 'action' , '' )
        self.action = action
        table_nice='???'

        self.tablib = table_cls(self.table)
        table_nice  = self.tablib.nice_name()
            

        self.infoarr['title']	= 'List action of ' + table_nice
       
        self.infoarr['layout'] = 'ADM/doc_list_act'
        self.infoarr['objtype'] = self.table
        self.infoarr['viewtype'] = 'list'
        self.infoarr['role.need'] = ['admin'] # allowed for content-admin
        self.infoarr['list.check_sel'] = 1
        self.infoarr['locrow'] = [
            {'url': 'ADM/home', 'text': 'Home'},
        ]

   
 
        
  
    def act_chown(self, db_obj, db_obj2, argu):
        """
        set MDO group of objects
        """
        
        table = self.table
        sql_from_order = self.sql_from_order
        
        try:
            user_id = int(argu.get('user_id', 0))
        except:
            user_id = 0
            
        if not user_id:
            self.setMessage('ERROR', 'No input "user_id" given.')


     
        modi_lib = oDOC.Modify_obj(db_obj)
     
        pk_col  = self.tablib.pk_col_get()
        sql_cmd = "x."+ pk_col +" from " + sql_from_order
        db_obj2.select_tuple(sql_cmd)  

        cnt=0
        infoarr=[]
        while db_obj2.ReadRow():
    
            objid  = db_obj2.RowData[0]
            try:
                modi_lib.set_obj(db_obj,objid)
                args = {
                    'vals': {
                        'DB_USER_ID': user_id
                    }
                }
                modi_lib.update(db_obj, args)
            except:
                message = str(sys.exc_info()[1])
                infoarr.append(['OBJ-ID:' + str(objid) + ' CH_OWN failed: ' + message])
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

            if action == 'chown':
                
                if int(self._req_data.get('go', 0)) < 1:
                    
                    self.data_out['form'] = {
                        'init': {
                            'title': 'Set new Owner for ' + str(objcnt) + ' documents?',
                            'submit.text': 'Set',
                            'editmode': 'edit',
                            'app.space.prefix': 'ADM/'
                        },
                        'hidden': {
                            "mod": self._mod,
                            "action": 'chown',
                            "go": 1,

                        },
                        'main': [{
                            'object': 'objlink',
                            'name': 'argu[user_id]',
                            'edit': 1,
                            'id': 1,
                            'val.nice': '',
                            'fk_t': 'DB_USER'
                        }
                        ]
                    }
                    break                
                
                self.act_chown(db_obj, db_obj2, self._req_data.get('argu', {}))
                break  
            
            self.setMessage('WARN', 'Action "'+action+'" unknown.')  
            
            break  # main loop break  
        
    
    def mainframe(self):
        
        db_obj  = self._db_obj1
        self.sh_main_layout(massdata=self.data_out)  