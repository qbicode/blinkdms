# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
default standard SINGLE object view 
- look for extension-file: plugin/ADM/o{TABLE}/obj_one.py
File:           obj_one.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
import traceback

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.obj.obj_info import Obj_info_lev2
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.obj_mod_meta import obj_mod_meta
from blinkdms.code.lib import f_module_helper
from blinkdms.code.lib.f_objhist import objhist
from blinkdms.code.lib.f_clip import clipboard
from blinkdms.code.lib.gui    import obj_one_sub
from blinkdms.ADM.plugin._sub import obj_one_gui
from blinkdms.code.lib.obj_one_IF import obj_one_IF

from   blinkdms.code.lib.oPROJ        import oPROJ
import blinkdms.code.lib.oPROJ.oPROJ_guisub as oPROJ_guisub



import sys, math

class plug_XPL(gPlugin) :  
    '''
     :var self._req_data:
      REQUIRED
       't'  : table 
       'id' : ID of object
       
      OPTIONAL:
       argu -- arguments
       editmode    : "view" | "edit" : show edit form?
       action :
         ['view']
         'update'
          'copy'
       view.tab.type: [home], meta
       tab : 
         ['default']
         'mod_log'
         'meta'
    '''
    
    editmode     = ''
    editmode_sum = 0 #(0 or 1) : summary editmode: editmode + obj_access_sum
    obj_ext_lib  = None # extender class
    table = ''
    objid = 0

    def register(self) :


        self.table = self._req_data.get('t','')
        self.objid = self._req_data.get('id',None)          


        self.infoarr['title']	 = 'main view'
        # self.infoarr['title2']	 = '[ID:'+str(self.objid)+']' + ' - single object of type: ' + table_nice
        self.infoarr['html']	 = 'ADM/home'
        self.infoarr['layout']	 = 'ADM/obj_one'
        self.infoarr['viewtype'] = 'object'
        self.infoarr['role.need'] = ['admin'] # allowed for content-admin
        self.infoarr['objtype'] = self.table
        self.infoarr['id']      = self.objid
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]        
        self.infoarr['js.scripts'] = ['x_modal.js'] 
        
        #TBD: check, if object exists ....
        
    def act_update(self, db_obj, argu):
        '''
        update object
        '''
        
        params =  { 'vals':{} }
        for col_xcode,val in argu.items():
            
            if col_xcode[0:2]=='x.':
                val_col = col_xcode[2:]            
                params['vals'][val_col] = val.strip()
            
        debug.printx(__name__, 'UPDATE:params: ' + str(params), 1)
        

        
        modlib = obj_mod_meta(db_obj,self.table, self.objid)
        modlib.update(db_obj, params)
        
        self.obj_ext_lib.update_after(db_obj)  # after update action
            
        self.setMessage('OK', 'Updated.')    
    
    def _get_projnames(self, db_obj, proj_answer):
        
        objlib_tmp = obj_abs('PROJ', 0)
        
        proj_names=[]
        cnt=0
        for proj_id in proj_answer['proj_arr']:
            
            if cnt>10:
                proj_names.append({'id':0, 'nice':'... more ...'})
                break
            
            if proj_id==proj_answer['proj_id_main']:
                continue
            
            objlib_tmp.set_objid(proj_id)
            nice = objlib_tmp.obj_nice_name(db_obj)
            proj_names.append({'id':proj_id, 'nice':nice})
            cnt=cnt+1
        
        return proj_names
    
    def act_copy(self, db_obj):
        """
        add object to clipboard
        """
        
        clip_lib = clipboard()
        clip_lib.reset()
        clip_lib.add( self.table, self.objid )
                
        self.setMessage('OK', 'Element copied to clipboard.')       
        
    def startMain(self) :
        
        db_obj = self._db_obj1
        self.infox = {}
        
        table_lib = table_cls(self.table)
        pk_num = len(table_lib.pk_cols())
        
        if pk_num>1:
            raise BlinkError(1, 'Only objects with ONE primary key are supported.')

        objhist_lib = objhist()
        objhist_lib.check_obj(self.table, self.objid)
        
        self.obj_writeacc_sum = 0
        obj_lib_lev2 = Obj_info_lev2( self.table, self.objid )
        self.obj_features = obj_lib_lev2.features(db_obj)
        self.obj_assocs   = obj_lib_lev2.assoc_info(db_obj)
        
        obj_acc_matrix    = self.objlib.obj_access(db_obj)
        if obj_acc_matrix["write"]>0:
            self.obj_writeacc_sum = 1
        
        # look for extension  
        self.obj_ext_lib = None
        
        if 'editmode' in self._req_data:
            self._session['sessvars']['o.'+self.table+'.editmode'] = self._req_data['editmode']        

        self.editmode = self._session['sessvars'].get('o.' + self.table + '.editmode', 'view')
        self.editmode_sum = 0
        if self.editmode == 'edit':  # and self.obj_writeacc_sum>0:
            self.editmode_sum = 1        
       
        module_path ='ADM/plugin/o'+ self.table +'/' + 'x_obj_one'
        module = f_module_helper.check_module(module_path,1)
        if module is not None:
            self.obj_ext_lib = module.extend_obj()   
        else:
            self.obj_ext_lib = obj_one_IF()    
            
        self.obj_ext_lib.set_vars(self._html, self.obj_features, self.table, self.objid, self._req_data)
        self.obj_ext_lib.init(db_obj)
        self.obj_ext_lib.set_IF_var('editmode', self.editmode)

       
        #debug.printx( __name__, 'META_X: ' + str(self._html._meta_content) ) 
        
        
        obj_nice    = self.objlib.obj_nice_name(db_obj)
        self._html.add_meta('obj.name', obj_nice )
        
        table_nice  = self.objlib.nice_name()
        self._html.add_meta('table.nice', table_nice )
        
        
        
        action = self._req_data.get('action', 'view')
        while 1:
            if action=='view':
                break # default 
            if action=='update':
                break # default             
            if action=='copy':
                self.act_copy(db_obj)
                break
            
            self.setMessage('WARN', 'Action "' + action + '" not implemented.')
            break
        
        if int( self._req_data.get('go', 0) ) > 0 :
            
            #debug.printx( __name__, 'UPDATE_Start: argu:' + str(self._req_data.get('argu', {} )) )
            
            if not len(self._req_data.get('argu', {} )):
                self.setMessage('WARN', 'No arguments given for update.') 
                return

            try:
                
                self.obj_ext_lib.update_pre(db_obj)  # pre update action
                debug.printx(__name__, 'STD2: self._req_data[argu]:' + str(self._req_data['argu']))
                self.act_update(db_obj, self._req_data.get('argu', {} ) )  
    
                self._req_data['go'] = '0'  # for restart ...
                self._req_data['action'] = 'view'
                self.restart = 1
                return
            
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()     
                message = str(exc_value)                 
                err_stack = traceback.extract_tb(exc_traceback)
                self.setMessage('ERROR', message, err_num=1, err_stack=err_stack)
                # continue ....              
                
        
        
        proj_answer = self.objlib.search_projects(db_obj)
        
        if  len(proj_answer['proj_arr']):
            proj_id       = proj_answer['proj_id_main']
            proj_lib      = oPROJ.mainobj(proj_id)    
            proj_path_arr = proj_lib.get_path_arr(db_obj)
            # path_str = oPROJ_guisub.show_path( proj_path_arr )
            
            self._html.add_meta('proj.path',  proj_path_arr  )
            
            if len(proj_answer['proj_arr'])>1:
                meta_info_tmp = self._get_projnames(db_obj, proj_answer)
                self._html.add_meta('proj.other',  meta_info_tmp  )
        
        self._html.add_meta('editmode',  self.editmode  )  
        self._html.add_meta('editmode_sum',  self.editmode_sum )  
        
          
    
    def mainframe(self):
        
        db_obj = self._db_obj1
        db_obj2= self.db_obj2()
        
        url_adder = '&t=' +self.table+'&id='+str(self.objid)
        base_url = '?mod=ADM/obj_one' + url_adder
        meta_url = '?mod=ADM/obj_meta'   + url_adder
        
        ed_active  =0
        view_active=1
        if self.editmode=='edit':
            ed_active  =1
            view_active=0        
        
        obj_gui_help = obj_one_gui.Mainobj( self.table, self.objid )
        nav = obj_gui_help.get_nav('main')
        self._html.add_meta('nav', nav)    
        
        menu = [
      
          {'title':'object', 'm_name':'object', 'submenu': 
               [
                {'title':'preferences',    'url': base_url,   'image.alias': 'settings' },
                {'title':'table description',  'url': '?mod=ADM/obj_one&t=CCT_TABLE&id=' + self.table ,   'image.alias': 'settings' },
               ]
          },
          {'title':'edit', 'm_name':'edit', 'submenu': 
              [ 
               { 'title':'Edit', 'url': base_url +'&editmode=edit', 'image.alias': 'edit-2', 'active': ed_active  },
               { 'title':'View', 'url': base_url +'&editmode=view', 'image.alias': 'eye',    'active': view_active  },
               { 'title':'copy',  'url':base_url +'&action=copy'   , 'image.alias' : 'copy' },
               { 'title':'list view', 'url':'?mod=ADM/obj_list&t='+ self.table   , 'image.alias' : 'align-justify' },

              ]
          }  , 
          {'title':'functions', 'm_name':'function', 'submenu': 
              [ 
              ]
          },
          {'title':'Mod Log', 'm_name':'mod_log', 'url': base_url +'&tab=mod_log'
          }           
        ]
             
        
        self.obj_ext_lib.mod_menu(menu)        
        
        self._html.add_meta('menu', menu)          
        # self._html.add_meta('view.tab.type', 'home' )
        
        columns_show = self.obj_ext_lib.get_columns()
        
        #debug.printx( __name__, 'obj_features: ' + str( self.obj_features) ) 
        #debug.printx( __name__, 'columns_show: ' + str( columns_show ) ) 
        
        for i in range(0,len(columns_show)):
            col_xcode = columns_show[i]['col']
            (prefix, col_raw) = obj_one_sub.Mainobj.col_xcode_split(col_xcode)
            if prefix == 'x':

                columns_show[i]['val'] = self.obj_features['vals'].get(col_raw,None)
            
        
        # create FORM data
        obj_gui_lib   = obj_one_sub.Mainobj(self.table, self.objid)
        self.data_out = obj_gui_lib.form_data2(db_obj, columns_show, self.editmode_sum)
 
        assoc_data = obj_gui_lib.assoc_data(self.obj_assocs)
        self.data_out['assoc'] = assoc_data
 
        debug.printx( __name__, 'self.data_out: ' + str(self.data_out) ) 

        self.obj_ext_lib.page_bottom(db_obj, db_obj2, self.data_out)
          
        self.sh_main_layout(massdata = self.data_out)    
        
        if self.obj_ext_lib is not None:
            self.obj_ext_lib.finish_ext()