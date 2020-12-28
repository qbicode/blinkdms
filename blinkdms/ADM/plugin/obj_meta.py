# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
SINGLE object : META view 
- look for extension-file: {TABLE}/obj_one.py
File:           obj_meta.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.obj.obj_info import Obj_info_lev2
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.obj_mod_meta import obj_mod_meta
from blinkdms.code.lib import oS_VARIO

#from blinkdms.code.lib import f_module_helper
from blinkdms.code.lib.gui    import obj_one_sub
from blinkdms.code.lib.gui    import form
from blinkdms.ADM.plugin._sub import obj_one_gui


class plug_XPL(gPlugin) :  
    '''
     :var self._req_data:
      REQUIRED
       't'  : table 
       'id' : ID of object
       'tab':
         'meta'
         'mod_log'
         'tab.descr'
         'vario'
        'go' : 0,1
    '''
    
    obj_ext_lib  = None # extender class

    def register(self):
    
        action = self._req_data.get('tab', '' )
        
        self.table = self._req_data.get('t','')
        
        if action=='tab.descr': 
            self.infoarr['viewtype'] = 'list'
        else:
            self.objid = self._req_data.get('id','')
            self.infoarr['viewtype'] = 'object'
            self.infoarr['id']	= self._req_data.get('id','')
      

        self.infoarr['title']	= 'Meta info'
       
        self.infoarr['layout']	= 'ADM/obj_meta'        
        self.infoarr['objtype'] = self._req_data.get('t','')

              
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]          
       
    def vario_form(self, db_obj, vario_data):
        
        all_defs = oS_VARIO.Methods.getAllKeysNice(db_obj, self.table ) 
       
        initarr   = {}
    
        initarr["title"]       = "Edit VARIO data"
        initarr["submittitle"] = "Save"
    
        hidden = {
                "mod":  self._mod,
                "t" :   self.table ,
                "id" :  self.objid,
                "tab" :  'vario',
            }       
    
        self.form_obj = form.form( initarr, hidden, 0)
    
        form_fields = []
        
        for key,key_nice in all_defs.items():
            
            val = vario_data.get(key,'')

            form_fields.append ( {
                    "title" : key_nice, 
                    "name"  : key,
                    "object": "text",
                    "val"   : val, 
                } )
            
            
        self.form_obj.set_form_defs( form_fields )        
    
    def vario_update(self, db_obj, new_vals):
        
        vario_mod = oS_VARIO.Modify_obj(db_obj, self.table, self.objid)
        
        for key,val in new_vals.items():
            vario_mod.updateKeyVal(db_obj, key, val)
            

    def startMain(self) :
        
        db_obj = self._db_obj1
        self.infox   = {}
        # self.dataout = {}
        self.data_out = {}
        self.nav_tab = self._req_data.get('tab', '' )
        
        go = int(self._req_data.get('go', '0' ))
        
        self._html.add_meta('tab', self.nav_tab )

       
        if self.nav_tab == 'tab.descr':
            # table description

            table_lib = table_cls('CCT_COLUMN')
            cols = table_lib.get_cols()

            sel_option = {'order': 'POS'}
            db_obj.select_col_vals('CCT_COLUMN', {'TABLE_NAME': self.table}, cols, sel_option)
            dataout_cols = []
            dataout_cols.append(cols)  # header

            while db_obj.ReadRow():
                out_row = []
                for col_def in cols:
                    val = db_obj.RowData[col_def]
                    out_row.append(val)
                dataout_cols.append(out_row)        
    
            self.data_out['main'] = {  
                'header': {
                    'title' : 'Table description'
                },
                # 'cols' : data_struct['cols'],
                'data' : dataout_cols
            }  
            
        if self.nav_tab == 'vario': 
            
            vario_vals = oS_VARIO.Methods.all_obj_data(db_obj, self.table, self.objid)
            self.vario_form(db_obj, vario_vals)            
            
            if go:
                self.form_obj.check_vals(self._req_data.get('parx', {} ))
                new_vals = self.form_obj.get_values_new()
                self.vario_update(db_obj, new_vals)
                
                self.setMessage('OK', 'VARIO data updated.' )
            
                # reload
                vario_vals = oS_VARIO.Methods.all_obj_data(db_obj, self.table, self.objid)
                self.vario_form(db_obj, vario_vals)
            
            self.data_out['vario'] = self.form_obj.get_template_data()
            
      
        debug.printx( __name__, 'MAIN: ' + str(self.data_out) )           
                     
    
    def mainframe(self):
        
        objid  = self.objid
        table  = self.table
        # db_obj = self._db_obj1
        
        obj_gui_help = obj_one_gui.Mainobj(table, objid)
        nav = obj_gui_help.get_nav( self.nav_tab )              
        self._html.add_meta('nav', nav )
       
        

        self.sh_main_layout( massdata = self.data_out)    
        
   