'''
user profile
'''

import sys

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib import oROLE
from blinkdms.code.lib.gui.form import form

class plug_XPL(gPlugin) :  
    '''
     * user profile
     * @package myprofile.py
     * @author  Steffen Kube (steffen@blink-dx.com)
     :param: id: DB_USER_ID: only allowed for root !!!
     :param parx: edit parameters
    '''

    def register(self) :
        
        # user_full  = self.infoarr['user.fullname']
        self.objid = self._session['sesssec']['user_id']
        self.table = 'DB_USER'
        if self._req_data.get('id','') !='': 
            self.objid = int(self._req_data.get('id',''))
            
        self.user_lib   = oDB_USER.mainobj(self.objid)
        user_full  = self.user_lib.get_fullname(self._db_obj1)                    

        self.infoarr['title']	= 'My profile: '+ str(user_full)
       
        self.infoarr['layout']	= 'ADM/myprofile'        
        self.infoarr['id']	= self.objid
        self.infoarr['objtype'] = self.table
        self.infoarr['viewtype'] = 'object'
        self.infoarr['role.need'] = ['admin'] # allowed for content-admin
              
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]          
        
    def act_update(self, db_obj, parx):
        
        if parx['PASS_WORD']=='':
            raise ValueError ('No password given.')
        
        if parx['PASS_WORD'] != parx['PASS_WORD_rep']:
            raise ValueError ('Password repeat is not the same.')
        
        hash_pw = self.user_lib.hash_pw(parx['PASS_WORD'])
        self.user_lib.verify_pw(hash_pw, parx['PASS_WORD'])
        
        params = { 
            'vals': {
                'EMAIL'    : parx['EMAIL'],
                'PASS_WORD': hash_pw,
                }
            }
        
        act_lib = oDB_USER.modify_obj(db_obj, self.objid)
        act_lib.update(db_obj, params)

        self.setMessage('OK', 'Updated.')

    def startMain(self) :
        
        db_obj = self._db_obj1
        
        user_lib = oDB_USER.mainobj(session['sesssec']['user_id'])
        admin = user_lib.has_role(db_obj, oROLE.ROLE_KEY_ADMIN)        

        if self._session['sesssec']['user_id'] != self.objid and (not admin):
            raise ValueError ('Onbly an admin can change the password of other users!')
        
        
        self.objlib = obj_abs('DB_USER', self.objid)
        col_arr=['EMAIL', 'NICK']
        self.features = self.objlib.main_feat_colvals(db_obj, col_arr)
        
        if self.features['NICK']=='root' and session['sesssec']['user']!='root':
            raise BlinkError (1, 'Only root can change its own password!')
        
        fields =   [
         {'name':'EMAIL'        , 'title': 'Email'    , 'object':'text', 'val':self.features['EMAIL'] },
         {'name':'PASS_WORD'    , 'title': 'Password' , 'object':'password', 'val':'', 'required':1},
         {'name':'PASS_WORD_rep', 'title': 'Password (repeat)' ,'object':'password', 'val':'', 'required':1}
         ]
        
        hidden = {
            "mod": self._mod,
            "id" : self.objid,
        }       
        
        self.form_obj = form( {}, hidden, 0)
        self.form_obj.set_form_defs( fields )        
        
        if int( self._req_data.get('go', 0) ) > 0 :
            
            # throws errors
            values_new = self.form_obj.check_vals( self._req_data.get('parx', {} ))
            self.act_update(db_obj, values_new )  
            
            self._html.forward( '?mod=ADM/obj_one&t=DB_USER&id=' + str(self.objid) , 'back to user')
                
        
    def mainframe(self):
        
        
        formdata = self.form_obj.get_template_data()
        
        menu = [
      
          {'title':'Password', 'm_name':'object', 'submenu': 
               [
                {'title':'Set password',  'jinja_inc': 'form.html' },
               
               ]
          },
          {'title':'Settings', 'm_name':'edit', 'submenu': 
              [ { 'title':'copy selected', 'image.alias': 'copy' }
              ]
          }  , 
                 
        ]        
        self._html.add_meta('menu', menu)  
        
        self.sh_main_layout(massdata = {'form':formdata} )    
