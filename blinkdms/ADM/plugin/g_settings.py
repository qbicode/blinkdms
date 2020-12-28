'''
Admin settings
'''

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from  blinkdms.code.lib.gui.form import form


import sys

class plug_XPL(gPlugin) :  
    '''
    
     * @package g_settings.py
     * @author  Steffen Kube (steffen@blink-dx.com)
    
     :param parx: edit parameters
    :params: 
      "action" :  
      
         'user_glob' : set some user globals, input: parx
    '''

    def register(self) :

        self.infoarr['title'] = 'General Settings'
        self.infoarr['layout'] = 'ADM/g_settings'
        self.infoarr['locrow'] = [{'url': 'ADM/home', 'text': 'Home'}]
        self.infoarr['role.need'] = ['admin'] # allow to admin group

            
    def act_user_glob(self, db_obj, parx):
        
         # create form fields
        form_fields = []
        userglobs = session['user_glob']
        
        field =   { 
                'title'  : 'Debug level' , 
                'name'   : 'debug.level' , 
                'object' : 'text', 
                'val'    : userglobs.get('debug.level', ''), 
                'notes'  : 'debug.level'
            }
        form_fields.append(field)
        
        
        hidden = {
            "mod": self._mod,
            "action" :  'user_glob',
        }   
        init= {
            'title': 'Set some User variables'
        }        
        
        self.form_obj = form( init, hidden, 0)
        self.form_obj.set_form_defs( form_fields )    
        
        if int( self._req_data.get('go', 0) ) > 0 :
            
            allow_cols = [
                'debug.level'
            ]
            
            for col in allow_cols:
                if col in parx:
                    session['user_glob'][col] = parx[col]

            self.setMessage('OK', 'Updated.')

            self._html.forward( '?mod=ADM/home' , 'back home')          

    def startMain(self) :
        
        db_obj = self._db_obj1
        
        action =  self._req_data.get('action', '')
        self._html.add_meta('action', action)
        
        if action=='':
            raise BlinkError(1,'No action given.')
       

        if action=='user_glob':
            parx  = self._req_data.get('parx', '')
            self.act_user_glob(db_obj, parx)         
                
        
    def mainframe(self):
        

        formdata = self.form_obj.get_template_data()
        self.sh_main_layout(massdata = {'form':formdata} )    
