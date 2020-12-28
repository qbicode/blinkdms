# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
profile
File:           profile.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib import oS_VARIO
#from blinkdms.code.lib.obj_mod_meta import Obj_mod_meta
#from blinkdms.code.lib import f_module_helper

from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.gui.form import form


class plug_XPL(gPlugin) :  
    '''
     :var self._req_data:
      REQUIRED
       't'  : table
       'argu': arguments
    OPTIONAL:
       'back_url' : urlencoded URL
    '''
    
    editmode     = ''
    editmode_sum = 0 #(0 or 1) : summary editmode: editmode + obj_access_sum
    obj_ext_lib  = None # extender class
    
    objid = 0

    def register(self) :


        self.table = 'DB_USER'
        self.table_lib = table_cls(self.table) 
        self.objid = session['sesssec']['user_id']

        self.infoarr['title']	 = 'My profile'
        self.infoarr['layout']	 = 'profile'
        self.infoarr['viewtype'] = 'tool' # this is a tool, because general checks except a mdo group
        # self.infoarr['objtype']  = self.table
        # self.infoarr['id']       = self.objid
        self.infoarr['locrow.auto'] = 0
        
    def act_update_pass(self, db_obj, parx):
        '''
        check VARIO: password.set.enable [1], -1
        '''
        
        
                
        if self.allow_change<0:
            raise BlinkError(1, 'You are not allowed to change the password. (Reason: VARIO:'+self.vario_key+'='+str(self.allow_change)+')')
        
        if parx['PASS_WORD']=='':
            raise BlinkError (2, 'No password given.')
        
        if parx['PASS_WORD'] != parx['PASS_WORD_rep']:
            raise BlinkError (3, 'Password repeat is not the same.')
        
        
        act_lib = oDB_USER.modify_obj(db_obj, self.objid)
        act_lib.ch_pwd(db_obj, parx['PASS_WORD'])

        self.setMessage('OK', 'Updated.') 
        
    def act_update_prof(self, db_obj, parx):
        '''
        update profile
        '''
        params = { 
            'vals':  parx 
            }
        
        act_lib = oDB_USER.modify_obj(db_obj, self.objid)
        act_lib.update(db_obj, params)

        self.setMessage('OK', 'Updated.')         
        
    def _form_pass(self):
        
        change_allow = 1
        
        if self.allow_change>=0:   
            pass
        
        else:
            
            change_allow = 0
            fields =   [
               { 'title': 'You cannot set the password (Reason: VARIO:'+self.vario_key+'='+str(self.allow_change)+')' , 'object':'text', 'val':'',  'edit':0}
             ]
            inits = {
                'editmode':'view'
            }        
        
        if  self.login_meth=='LOCAL':   
            pass
        
        else:
            
            change_allow = 0
            fields =   [
               { 'title': 'Password cannot be set. You are using a remote authentication server.' , 'object':'text', 'val':'',  'edit':0}
             ]
            inits = {
                'editmode':'view'
            }
            
        if change_allow:
            
            fields =   [
             {'name':'PASS_WORD'    , 'title': 'Password' , 'object':'password', 'val':'', 'required':1},
             {'name':'PASS_WORD_rep', 'title': 'Password (repeat)' ,'object':'password', 'val':'', 'required':1}
             ]
            inits={}            
        
        hidden = {
            "mod": self._mod,
            "action" : 'pass',
        }       
        
        self.form1_obj = form( inits, hidden, 0)
        self.form1_obj.set_form_defs( fields )
        
    def _form_profile(self):
        
        fields =   [
         {'name':'EMAIL'        , 'title': 'Email'   , 'object':'text', 'val':self.features['EMAIL'] },
        #NOT allowed du to CFR820 Part11:  {'name':'FULL_NAME'    , 'title': 'Name'    , 'object':'text', 'val':self.features['FULL_NAME'] },
         
        ]
        
        hidden = {
            "mod": self._mod,      
            "action" : 'profile',
        }       
        
        self.form2_obj = form( {}, hidden, 0)
        self.form2_obj.set_form_defs( fields )  
        
    def _form_info(self, db_obj):
        '''
        user info form
        '''
        
        
        
        roles_arr_raw = self.user_lib.get_role_names(db_obj)
        roles_arr = []
        for row in roles_arr_raw:
            roles_arr.append(row[1])
        roles_text = ', '.join(roles_arr)
        
        fields = [
            {  'title': 'User Name', 'object': 'text', 'val': self.infoarr['user.fullname'], 'edit':0},
            {  'title': 'Email'    , 'object':'text', 'val': self.features.get('EMAIL','?'), 'edit':0 },
            {  'title': 'Roles'    , 'object':'text', 'val': roles_text, 'edit':0 },
            {  'title': 'Login method'    , 'object':'text', 'val': self.login_meth, 'edit':0  }
        ]
        
        hidden = {
            "mod": self._mod,      
        }       
        
        self.form3_obj = form( { 'editmode': 'view' }, hidden, 0)
        self.form3_obj.set_form_defs( fields )  
    
    def startMain(self) :
        
        db_obj = self._db_obj1
        
        self.objlib = obj_abs('DB_USER', self.objid)
        col_arr=['EMAIL','FULL_NAME']
        self.features = self.objlib.main_feat_colvals(db_obj, col_arr)
        self.user_lib = oDB_USER.mainobj(self.objid)
        self.login_meth = self.user_lib.get_login_method(db_obj)
        
        self.vario_key    = 'password.set.enable'
        self.allow_change = oS_VARIO.Methods.obj_data_by_key(db_obj, 'DB_USER', self.objid, self.vario_key)
        if self.allow_change==None:
            self.allow_change = 1
        else:
            try:   
                self.allow_change = int(self.allow_change)
            except:
                self.allow_change = 1 # fallback    
        debug.printx( __name__, '194)allow_change:' + str(self.allow_change) )    
        
        self._form_pass()  
        self._form_profile()
        self._form_info(db_obj)
        
        if int( self._req_data.get('go', 0) ) > 0 :
            
            if  self._req_data.get('action', '') =='pass' :
                # throws errors
                values_new = self.form1_obj.check_vals( self._req_data.get('parx', {} ))
                self.act_update_pass(db_obj, values_new )  
 
                
            if  self._req_data.get('action', '') =='profile' :
                # throws errors
                values_new = self.form2_obj.check_vals( self._req_data.get('parx', {} ))
                self.act_update_prof(db_obj, values_new )  
                
            
            self._html.forward( '?mod=profile' , 'back to profile')            

    
    def mainframe(self):
        
        
        form1_data = self.form1_obj.get_template_data()
        form2_data = self.form2_obj.get_template_data()
        form3_data = self.form3_obj.get_template_data()
        
        sysdata = []
        sysdata.append(['Development site', '<a href="https://github.com/qbicode/blinkdms">BlinkDMS</a>'])
        sysdata.append(['Application version', session['sesssec']['SW_Version']])
        
        sysinfo = {
            'header': { 
                'title':'System info'
            }, 
            'opt': {
              'safe': 1
            },
            'data': sysdata
            
        }
        
        menu = [
      
          
          {'title':'Settings', 'm_name':'edit', 'submenu': 
              [ { 'title':'copy selected', 'image.alias': 'copy' }
              ]
          }  , 
          {'title':'Password', 'm_name':'object', 'submenu': 
               [
                {'title':'Set password',  'jinja_inc': 'form.html' },
               
               ]
          },          
                 
        ]        
        self._html.add_meta('menu', menu)  
        
        self.sh_main_layout(massdata = {'form1':form1_data, 'form2':form2_data, 'form3':form3_data, 'sysinfo': sysinfo } )    
    
 
        
        