# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
default standard list view 
- look for extension-file: o{TABLE}/x_obj_list.py
File:           obj_list.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.tab_abs_sql import Table_sql
from blinkdms.code.lib import f_module_helper
from blinkdms.code.lib.f_clip import clipboard
from blinkdms.code.lib.obj_list_IF import obj_list_IF


from blinkdms.code.lib.oPROJ.clip_coll import clip_coll 
from blinkdms.code.lib.obj.table_out import table_show 
from blinkdms.code.lib.gui.obj_list_sub import Obj_list_sub

import sys, traceback


                
class plug_XPL(gPlugin) :  
    '''
     * @package folder.py
     * @author  Steffen Kube (steffen@blink-dx.com)
     :var self._req_data:
       't' : table 
       'page_no' : show this page number [1]
       'q' : dict of new query conditions
         'new' : 0,1 : reset query
         'proj_id' : if set: get objects from project (and reset query)
         'op'
         'logop'
         'col'
         'val'
       'sel' : list of IDs
       'modal' = {} : modal action
          'id' : ID of javascript-object (NUMBER)
       'action':
         'view'
         'copy'
         'copycl' : add to clipboard collection
         'export'
    '''
    
    action=''
    obj_ext_lib = None
    list_struct = {} # see table_out.py: list_struct_STRUCT
    

    def register(self) :
        
        action = self._req_data.get( 'action' , 'view' )
        self.action = action
        table_nice='???'
        self.tablib = None
        if 't' not in self._req_data:
            self.table = ''
        else:
            
            self.table  = self._req_data['t']
            self.tablib = table_cls(self.table)
            table_nice  = self.tablib.nice_name()
            

        self.infoarr['title']	= 'List view of ' + table_nice
       
        self.infoarr['layout']	= 'ADM/obj_list'
        self.infoarr['objtype'] = self.table
        self.infoarr['role.need'] = ['admin'] # allowed for content-admin
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]
        self.infoarr['js.scripts'] = ['x_menu2.js', 'x_modal.js']
        
        if self._req_data.get( 'modal', None ) is not None:
            self.infoarr['html'] = 'ADM/plugpure' # slim GUI ...
        
        if action=='export':
            self.infoarr['gui'] = -1
   
    def act_copy(self, db_obj, sql_from_order):
        """
        add objects to clipboard
        """
        
        clip_lib = clipboard()
        clip_lib.reset()
        
        pk_col = self.tablib.pk_col_get()
        sql_cmd = "x."+ pk_col +" from " + sql_from_order
        db_obj.select_tuple(sql_cmd)  
        
        cnt=0
        while db_obj.ReadRow():
    
            objid  = db_obj.RowData[0]
            clip_lib.add( self.table, objid )
            cnt = cnt + 1        
            
        self.setMessage('OK', str(cnt) + ' Elements copied to clipboard.')  
         
         
    def startMain(self) :
        
        db_obj  = self._db_obj1
        db_obj2 = self.db_obj2()
        
        self.default_run    = 1
        self.list_struct    = {}
        
        self.list_struct['meta'] = {}
        
        table = self.table
        
        sql_select_lib = Table_sql(table)
        query_cond      = self._req_data.get( 'q',{} )
        page_now        = int(self._req_data.get('page_no',1))
        
        self.list_struct['page_no'] = page_now
        
        if int(query_cond.get('new',0))>0 or query_cond.get('logop','')=='NEW':
            sql_select_lib.reset()
            sql_select_lib.save_session()
            
        if int(query_cond.get('new',0))>0:
            query_cond.pop('new') # remove the key
            
        debug.printx( __name__, 'query_cond: ' + str(query_cond) )
            
        if int(query_cond.get('proj_id',0))>0:
            sql_select_lib.reset()   
            query_cond['proj_id'] = int(query_cond['proj_id']) # convert to integer ...
            
        if len(self._req_data.get( 'sel', [] ) ):
            sql_select_lib.reset()
            query_sel = self._req_data['sel']
            sql_select_lib.set_selection(query_sel)
            # debug.printx( __name__, 'SEL: ' + str(query_sel) )   
            sql_select_lib.save_session()
        
        if len(query_cond) : 
            answer = sql_select_lib.check_one_condition(query_cond)
            if not answer['valid']:
                self.setMessage('ERROR', 'Input-Error: '+ answer['message'])
                sql_select_lib = Table_sql(table)  # reset all INPUTS from form
            else:
                sql_select_lib.add_condition(query_cond)
                sql_select_lib.save_session()
        
        self._html.add_meta('q.filter_active', sql_select_lib.filter_is_active() )
        self.sql_from       = sql_select_lib.get_sql_from(db_obj)
        self.sql_from_order = sql_select_lib.get_sql_from_order(db_obj)
        sql_nice = sql_select_lib.get_sql_nice()
        
        debug.printx( __name__, 'SQL: ' + self.sql_from )
        
        sql_cmd = "count(1) from " + table
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        self.list_struct['objcnt'] = db_obj.RowData[0]          
        
        try:
            sql_cmd = "count(1) from " + self.sql_from
            db_obj.select_tuple(sql_cmd)
            db_obj.ReadRow()
            objcnt_sel = db_obj.RowData[0]  
            self.list_struct['objcnt_sel'] = objcnt_sel           
            
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = str(exc_value) 
            err_stack = traceback.extract_tb(exc_traceback)
            self.setMessage('ERROR', 'Error on SQl-Filter: ' + message,  err_stack=err_stack)
            self.default_run = 0
            self.list_struct['objcnt_sel'] = 0
            return
        
        self._html.add_meta('q.sql_where',  sql_nice  )
        
        action = self._req_data.get( 'action' , 'view' )
        debug.printx( __name__, 'ACTION: ' + action )
        
        while 1:
            if  action=='view':
                break
            
            if  action=='copy':
                self.act_copy(db_obj, self.sql_from_order)
                break
            
                     
                
            if  action=='copycl' and table=='EXP':
                MAX_COPY_CNT = 2000
                
                
                if not objcnt_sel:
                    self.setMessage('WARN', 'No Elements selected.')
                    break
                    
                if  objcnt_sel> MAX_COPY_CNT:
                    self.setMessage('WARN', 'Too many Elements selected. Max '+str(MAX_COPY_CNT)+' allowed.')
                    break
                    
                clip_obj  = clip_coll(db_obj)
                clip_proj = clip_obj.get_proj_id()
                cnt = clip_obj.add_objects_sql(db_obj, db_obj2, table, self.sql_from_order)
                
                clip_cnt = clip_obj.get_obj_num(db_obj, table)
                if 'clip_coll' not in self._session['sessvars']:
                    self._session['sessvars']['clip_coll'] = { 'proj': clip_proj }
                self._session['sessvars']['clip_coll']['EXP'] = clip_cnt
                
                self.setMessage('OK', str(cnt) + ' objects copied to clipboard-collection.')  
                break
            
            self.setMessage('WARN', 'Action "'+action+'" unknown. Under construction.')  
            
            break  # main loop break  


        self.obj_ext_lib = None
        # check for OBJECT specific library
        module = f_module_helper.check_module( 'ADM/plugin/o'+ table +'/x_obj_list', 1)
        if module is not None:
            # extend class obj_list_IF
            self.obj_ext_lib = module.extend_obj() 
        else:
            self.obj_ext_lib = obj_list_IF()
        self.obj_ext_lib.set_vars(table)
                    
    
    def mainframe(self):
        
        db_obj  = self._db_obj1
        db_obj2 = self.db_obj2()
        
        modal_info  = self._req_data.get( 'modal', None )
        debug.printx( __name__, 'modal_info: ' + str(modal_info) )   
    
        
        if 'clip_coll' not in self._session['sessvars']:
            clip_obj  = clip_coll(db_obj)
            
            if clip_obj.has_clip_proj():
                clip_proj = clip_obj.get_proj_id()
                self._session['sessvars']['clip_coll']= { 'proj': clip_proj }
                
                clip_cnt = clip_obj.get_obj_num(db_obj, self.table) 
                self._session['sessvars']['clip_coll']['EXP'] = clip_cnt
                self._html.add_meta('clip_coll',  { 'EXP': self._session['sessvars']['clip_coll']['EXP'] , 
                        'proj': self._session['sessvars']['clip_coll']['proj'] } )
        
        cnt_per_page = 20

        menu = [
      
          {'title':'object', 'm_name':'object', 'submenu': 
               [
                {'title':'preferences',  'url':'?mod=ADM/obj_list_pref&t='+self.table,   'image.alias': 'settings' },
                {'title':'export data',  'url':'javascript:formx("export")', 'image.alias': 'download' },
                {'title':'new object',  'url':'?mod=ADM/obj_new&t='+self.table, 'image.alias': 'plus' },
                {'title':'delete object',  'url':'?mod=ADM/obj_list_act&t='+self.table+'&action=delete', 'image.alias': 'x' },
                {'title':'Table Description',  'url':'?mod=ADM/obj_one&t=CCT_TABLE&id=' + self.table, 'image.alias': 'settings' },
                
               ]
          },
          {'title':'edit', 'm_name':'edit', 'submenu': 
              [ 
               { 'title':'select checked', 'url':'javascript:formx("view")'  , 'image.alias': 'check-square' },
               { 'title':'copy selected', 'url':'javascript:formx("copy")'   , 'image.alias' : 'copy' },
              
              ]
          }  , 
          {'title':'functions', 'm_name':'func', 'submenu': 
              [ 
              ]
          }  ,                  
        ]
        
        if self.obj_ext_lib is not None:
            self.obj_ext_lib.mod_menu(menu)        
        
       
        self._html.add_meta('menu', menu)  
        
        self._html.add_meta('table',   self.table  )
        
        self.list_struct['cnt_per_page'] = cnt_per_page
        self._html.add_meta('cnt.select',   self.list_struct['objcnt_sel'] )
        self._html.add_meta('cnt.all',      self.list_struct['objcnt'] )
        self._html.add_meta('cnt_per_page', self.list_struct['cnt_per_page'] ) 
        
        admin_area=1
        list_helper   = Obj_list_sub(self.table, admin_area)
        columns_show  = list_helper.get_col_prefs()
        filter_cols   = list_helper.filter_columns_get(db_obj, columns_show)
        self._html.add_meta('q.cols', filter_cols)
        
      
        self.list_struct['columns'] = columns_show        
        
        if self.default_run:
            
            htmltab_lib = table_show(self.table, self.list_struct, [], admin_area)
            tab_opt = {'modal_info' : modal_info}
            htmltab_lib.show(db_obj, db_obj2, ' from ' + self.sql_from_order, tab_opt)
            meta_struct = htmltab_lib.get_meta()
            self._html.meta_merge(meta_struct)
            
            debug.printx( __name__, '_meta_content: ' + str(self._html._meta_content) )
        
        if  self.action=='export':
            from blinkdms.code.lib import obj_export
            export_lib =  obj_export.Main(self.table, self._html) 
            export_lib.do(self.list_struct)
        else:
            self.sh_main_layout(massdata = self.list_struct)  