# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
list actions 
File:           obj_list_act.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
from blinkapp.code.lib.main_imports import *
from blinkapp.code.lib.app_plugin import gPlugin
from blinkapp.code.lib.tab_abs_sql  import table_sql
from blinkapp.code.lib.f_clip import clipboard
from blinkapp.code.lib.obj_mod_meta import obj_mod_meta

from blinkapp.code.lib.gui.obj_list_sub import Obj_list_sub
from blinkapp.code.lib.oDB_USER import oDB_USER

import sys, traceback


                
class plug_XPL(gPlugin) :  
    '''
     * @package folder.py
     * @author  Steffen Kube (steffen@blink-dx.com)
     :var self._req_data:
       't' : table     
       'action':
         'delete'
         'set_mdo' : set MDO group
    '''
    
    action=''

    

    def register(self) :
        
        action = self._req_data.get( 'action' , '' )
        self.action = action
        table_nice='???'
        self.tablib = None
        if 't' not in self._req_data:
            self.table = ''
        else:  
            self.table  = self._req_data['t']
            self.tablib = table_cls(self.table)
            table_nice  = self.tablib.nice_name()
            

        self.infoarr['title']	= 'List action of ' + table_nice
       
        self.infoarr['layout']	= 'ADM/obj_list_act'
        self.infoarr['objtype'] = self.table
        self.infoarr['viewtype']= 'list'
        self.infoarr['list.check_sel'] = 1
        self.infoarr['js.scripts']  =  ['x_modal.js']    
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]

   
 
        
    def act_delete(self, db_obj, db_obj2, sql_from_order):
        """
        delete objects
        """
        
        table = self.table
        
        # check role rights
        user_id    = session['sesssec']['user_id']
        user_lib   = oDB_USER.mainobj(user_id)
        acc_matrix = user_lib.role_rights_tab(db_obj, table)
        if not acc_matrix['delete']:
            raise BlinkError(4, 'You have no "delete" right for this table.')         
     
        modi_lib = obj_mod_meta(db_obj,table, None)
     
        pk_col  = self.tablib.pk_col_get()
        sql_cmd = "x."+ pk_col +" from " + sql_from_order
        db_obj2.select_tuple(sql_cmd)  

        cnt=0
        infoarr=[]
        while db_obj2.ReadRow():
    
            objid  = db_obj2.RowData[0]
            try:
                modi_lib.set_obj(db_obj,objid)
                modi_lib.delete(db_obj)
            except:
                message = str(sys.exc_info()[1])
                infoarr.append( ['OBJ-ID:'+str(objid)+' delete failed: ' + message] )
            cnt = cnt + 1        
        
        if len(infoarr):
            self.setMessage( 'ERROR', str(len(infoarr)) + ' Problem(s) occurred.') 
            self._html.add_meta('error_list', infoarr )
            
        self.setMessage('OK', str(cnt) + ' Elements deleted.') 
        
    def act_set_mdo(self, db_obj, db_obj2, sql_from_order, argu):
        """
        set MDO group of objects
        """
        
        table = self.table
        
        try:
            mdo_grp = int(argu.get('mdo_grp', 0))
        except:
            mdo_grp = 0
            
        if not mdo_grp:
            self.setMessage('ERROR', 'No input given.')
        
        debug.printx( __name__, 'MDO: ' + str(mdo_grp) )
        
        # check role rights
        user_id    = session['sesssec']['user_id']
        user_lib   = oDB_USER.mainobj(user_id)
        acc_matrix = user_lib.role_rights_tab(db_obj, table)
        if not acc_matrix['write']:
            raise BlinkError(4, 'You have no "write" right for this table.')         
     
        modi_lib = obj_mod_meta(db_obj,table, None)
     
        pk_col  = self.tablib.pk_col_get()
        sql_cmd = "x."+ pk_col +" from " + sql_from_order
        db_obj2.select_tuple(sql_cmd)  

        cnt=0
        infoarr=[]
        while db_obj2.ReadRow():
    
            objid  = db_obj2.RowData[0]
            try:
                modi_lib.set_obj(db_obj,objid)
                args={
                    'access': {
                        'OWN_GRP_ID': mdo_grp
                    }
                }
                modi_lib.update(db_obj, args)
            except:
                message = str(sys.exc_info()[1])
                infoarr.append( ['OBJ-ID:'+str(objid)+' SET_MDO failed: ' + message] )
            cnt = cnt + 1        
        
        if len(infoarr):
            self.setMessage( 'ERROR', str(len(infoarr)) + ' Problem(s) occurred.') 
            self._html.add_meta('error_list', infoarr )
            
        self.setMessage('OK', str(cnt) + ' Elements modified.') 
         
         
    def startMain(self) :
        
        db_obj  = self._db_obj1
        db_obj2 = self.db_obj2()
    
       
        table = self.table
        
        sql_select_lib  = table_sql(table)
        
        self.data_out = {}

        
        self.sql_from       = sql_select_lib.get_sql_from(db_obj)
        self.sql_from_order = sql_select_lib.get_sql_from_order(db_obj)
        sql_nice = sql_select_lib.get_sql_nice()
        
        debug.printx( __name__, 'SQL: ' + self.sql_from )
        
        pk_col = self.tablib.pk_col_get()
        sql_cmd = "count(1) from " + self.sql_from
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        objcnt  = db_obj.RowData[0]        

        action = self._req_data.get( 'action' , '' )
        debug.printx( __name__, 'ACTION: ' + action )
        
        while 1:
            
            if  action=='delete':
                
                if int(self._req_data.get('go', 0)) < 1:
                    self.data_out['form'] = {
                        'init': { 'title':'Do you want to delete '+str(objcnt)+' objects?', 'submit.text':'Delete', 'editmode':'edit' },
                        'hidden': {
                            "mod": self._mod,
                            "t"  : table,
                            "action" :  'delete',
                            "go": 1,
                           
                        },
                        'main': [  ]
                    }
                    break                
                
                self.act_delete(db_obj, db_obj2, self.sql_from_order)
                break  
            
            if  action=='set_mdo':
                
                if int(self._req_data.get('go', 0)) < 1:
                    self.data_out['form'] = {
                        'init': { 
                            'title':'Set MDO-Group for '+str(objcnt)+' objects?',
                            'submit.text':'Set', 
                            'editmode':'edit',
                            'app.space.prefix': 'ADM/'
                            },
                        'hidden': {
                            "mod": self._mod,
                            "t"  : table,
                            "action" :  'set_mdo',
                            "go": 1,
                           
                        },
                        'main': [ {
                            'object':'objlink',
                            'name': 'argu[mdo_grp]',
                            'edit':1,
                            'id':1,
                            'val.nice': '',
                            'fk_t':'USER_GROUP'   
                            }
                        ]
                    }
                    break                
                
                self.act_set_mdo(db_obj, db_obj2, self.sql_from_order, self._req_data.get('argu', {}))
                break  
            
            self.setMessage('WARN', 'Action "'+action+'" unknown.')  
            
            break  # main loop break  
        
    
    def mainframe(self):
        
        db_obj  = self._db_obj1
        self.sh_main_layout(massdata=self.data_out)  