# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
default standard SINGLE object CREATOR 
File:           obj_new.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.gui.form import form
from blinkdms.code.lib.obj_mod_meta import obj_mod_meta
from blinkdms.code.lib import f_module_helper
from blinkdms.code.lib.obj_one_IF import obj_new_IF
from blinkdms.code.lib.gui    import obj_one_sub

import sys, math

class plug_XPL(gPlugin) :  
    '''
     :var self._req_data:
      REQUIRED
       't'  : table 
       'go' : 0,1
       'proj_id' : add to project id
    '''
    
    obj_ext_lib = None


    def register(self) :
        
        table_nice= '???'
        
        db_obj = self._db_obj1
        self.table = self._req_data.get('t','')
        self.table_lib = None
        
        if self.table != '' :
            self.table_lib = table_cls(self.table)
            
 

        self.infoarr['title']	= 'Create Object' 
       
        self.infoarr['layout']	= 'ADM/obj_new'
        self.infoarr['objtype'] = self.table
        self.infoarr['viewtype'] = 'list'
        self.infoarr['role.need'] = ['admin']  # allowed for content-admin
        self.infoarr['objtab.acc_check'] = {'tab': ['insert']}  # check this TABLE right !!!
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]    
        self.infoarr['js.scripts'] = ['x_modal.js']
        
    def act_new(self, db_obj, argu, options={} ):
        '''
        create the object
        '''
        
        params =  {}
        for col_xcode,val in argu.items():
            
            (prefix, val_col) = obj_one_sub.Mainobj.col_xcode_split(col_xcode)

            if prefix=='x':
                if 'vals' not in params:
                    params['vals'] = {}
                params['vals'][val_col] = val
        
        new_options={}
        if options.get('proj_id',0):
            new_options['proj_id'] = options.get('proj_id',0)
            
        debug.printx(__name__, "(74) params:"+str(params) )
       
        
        modlib = obj_mod_meta(db_obj,self.table)
        objid  = modlib.new(db_obj, params, new_options)
        
        self.obj_ext_lib.new_after(db_obj, objid)
            
        self.setMessage( 'OK', 'Object Created. ID:'+str(objid) )   
        
        return objid
 
    def startMain(self) :
        
        db_obj = self._db_obj1
        self.infox = {}
        
        proj_id = int(self._req_data.get('proj_id',0))
        self._html.add_meta('table', self.table )
        self._html.add_meta('proj_id', proj_id )
        
        table_nice  = self.table_lib.nice_name()
        self._html.add_meta('table.nice', table_nice )
        
        # look for extension  
        self.obj_ext_lib = None
    
        module_path ='ADM/plugin/o'+ self.table +'/' + 'x_obj_one'
        module = f_module_helper.check_module(module_path, 1)
        if module is not None:
            if f_module_helper.module_has_class(module, 'extend_new'):
                self.obj_ext_lib = module.extend_new() 
        
        if self.obj_ext_lib == None:
            self.obj_ext_lib = obj_new_IF()
                
        self.obj_ext_lib.set_vars(self._html, self.table)     
        self.obj_ext_lib.init(db_obj)
 
        
        # self.form_obj = form( {}, hidden, 0)
        # fields = []
        tablib = table_cls(self.table)
        pk_name = tablib.pk_col_get()
        
        columns_show = self.obj_ext_lib.get_columns()
        
        # modify columns_show
        for i in range(0,len(columns_show)):
            row = columns_show[i]
            column = row['col']
            #col_vals[column] = None
            
            (prefix, col_raw) = obj_one_sub.Mainobj.col_xcode_split(column)
            if prefix=='x':  
                # allow EDIT, if primary key is a NAME
                col_def = tablib.col_def(col_raw)
                if col_def['APP_DATA_TYPE'] == 'NAME' and col_def['PRIMARY_KEY'] == 1:
                    columns_show[i]['EDITABLE'] = 1
        
        #obj_features_in = {
        #  'vals': col_vals
        #}
        
        # create FORM data
        #
        # !!! TBD: must be rewritten: see hubd/plugin/obj_new.py
        #
        editmode = 1

        obj_gui_lib   = obj_one_sub.Mainobj(self.table, self.objid)
        self.data_out = obj_gui_lib.form_data2(db_obj, columns_show, editmode)   
        self.data_out['form']['init']['submit.text'] = 'Create'
        
        
        if int( self._req_data.get('go', 0) ) > 0 :
            
            
            # OLD: values_new = self.form_obj.check_vals( self._req_data.get('parx', {} ))

            values_new = self._req_data.get('argu', {} )

            self.obj_ext_lib.set_data(values_new)
            self.obj_ext_lib.check_data(db_obj)
            
            new_opt = {'proj_id':proj_id}
            
            objid = self.act_new(db_obj, values_new, new_opt )                
            
            req_data = {
                'mod': 'ADM/obj_one',
                't':self.table,
                'id': objid
            }
            self.forward_internal_set(req_data)
            
            # self._html.forward( '?mod=ADM/obj_one&t='+self.table+'&id=' + str(objid) , 'go to object')           
        
    
    def mainframe(self):

          
        # formdata = self.form_obj.get_template_data()
        
        self.sh_main_layout(massdata = self.data_out )           