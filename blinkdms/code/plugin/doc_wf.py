# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
workflow actions
File:           doc_wf.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oVERSION import oVERSION_edit
from blinkdms.code.lib.oVERSION import oVERSION_WFL
from blinkdms.code.lib.oSTATE import oSTATE
from blinkdms.code.lib import login
from blinkdms.code.lib.gui.form import form
from blinkdms.code.lib import oROLE



class plug_XPL(gPlugin):
    '''
     :var self._req_data:
       'id' : VERSION-ID
       'act' 
          'r_start' : release workflow start
          'e_start' : edit workflow start
          'sign'
          'reject'  : do a singel reject
          'v_new' : new version
        'parx' : for 'sign'
        'state_key' : key of state
    '''
  
    obj_ext_lib  = None # extender class

    def register(self):

        idtmp = self._req_data.get('id', 0)
        try:
            self.objid = int(idtmp)
        except:
            self.objid = 0

        self.infoarr['title'] = 'Workflow action: ' + self._req_data.get('act', '')
        self.infoarr['layout'] = 'doc_wf'
        self.infoarr['viewtype'] = 'object'
        self.infoarr['objtype'] = 'VERSION'
        self.infoarr['id'] = self.objid
        self.infoarr['obj.id_check'] = 1
        self.infoarr['locrow.show_mo']=1
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT]
        self.infoarr['context.allow'] = ['EDIT']        

    def form_sign(self, data):
        '''
        opt: H_STATE_ID:  review, reject
        '''

        state_id = int(data.get('STATE_ID', '0'))
        if state_id:
            row = self.states_by_id[state_id]
            state_key = row['NAME']
        else:
            
            state_key = 'REVIEW'
            row = self.states_by_key[state_key]
            state_id = row['STATE_ID']

        if state_key != 'REJECT':
            self.massdata['reject.button.show'] = 1

        fields = [
         {'title': 'Set Status', 'edit': 0, 'object': 'text', 'val': row['NICE'] },
         {'name': 'NOTES', 'title': 'Notes', 'edit': 1, 'object': 'textarea', 'required': 0, 'val': data.get('NOTES', '')},
        ]
        
        if self.do_check_pw:
            fields.append( {'name': 'password', 'title': 'Password', 'edit': 1, 'object': 'password', 'required': 1, 'val': '', 'required':1 } )
        
        hidden = {
            "mod": 'doc_wf',
            "act": 'sign',
            'id': self.objid,
            'parx[STATE_ID]': '',
        }
        init = {
        }

        self.form_obj = form(init, hidden, 0)
        self.form_obj.set_form_defs(fields)
        
        form_data = self.form_obj.get_template_data()

        self.massdata['form.state.STD'] = state_id
        self.massdata['form.state.REJECT'] = self.states_by_key['REJECT']['STATE_ID']
        
        self.massdata['form'] = form_data    

    def startMain(self):

        db_obj = self._db_obj1
        self.do_check_pw = 0
        self.do_check_pw = session['globals'].get('workflow.sign.password.need',0)
        
        self.massdata = {'form': {}}

        objlib = oVERSION_edit.Mainobj(db_obj, self.objid)
        features = objlib.features(db_obj)
        action = self._req_data.get('act', '')

        if not objlib.is_current_versid(db_obj):
            raise BlinkError(1, 'This version is not valid for Edit!')
            
        

        worflow_obj = oVERSION_WFL.Modify_obj(db_obj, self.objid)
        self.states_by_key = oSTATE.STATE_info.get_all_by_key(db_obj)
        self.states_by_id = oSTATE.STATE_info.get_all_by_id(db_obj)
        do_forward = 0

        if action == 'r_start':

           
            if objlib.workflow_is_active(db_obj):
                raise BlinkError(2, 'Workflow already active.')

            worflow_obj.start_r_wfl(db_obj)

            self._html.setMessage('OK', 'Workflow started.')
            do_forward = 1

        if action == 'sign':
    
            if not objlib.workflow_is_active(db_obj):
                raise BlinkError(3, 'Workflow not active.')

            parx = self._req_data.get('parx', {})

            if int(self._req_data.get('go', '0')) > 0:
                
                if self.do_check_pw:
                    
                    session_dummy= {}
                    login_obj = login.login(session_dummy)
                    login_obj.check_verify(db_obj, session['sesssec']['user'], parx['password'])
                    del(parx['password']) # not allowed on audit log
                
                worflow_obj.sign(db_obj, parx)
    
                self._html.setMessage('OK', 'Signed.')
                do_forward = 1
            else:
                if self._req_data.get('state_key', '') != '':
                    state_key = self._req_data.get('state_key', '')
                    state_id_tmp = self.states_by_key[state_key]['STATE_ID']
                    parx['STATE_ID'] = state_id_tmp
                self.form_sign(parx)

        if action == 'v_new':
            
            #TBD: test, if version already started ...
            if objlib.is_released(db_obj):
                debug.printx(__name__, '(167): is released.')
        
            else:
                raise BlinkError(1, 'This old Version is not released.')

            version_lib = oVERSION.Modify_obj(db_obj)
            new_vers_id = version_lib.new_successor(db_obj, self.objid)

            self._html.setMessage('OK', 'New Version created.')
            req_data = {
                'mod': 'doc_edit',
                'id': new_vers_id
            }
            self.forward_internal_set(req_data)

        if do_forward:
            req_data = {
                'mod': 'doc_edit',
                'id': self.objid
            }
            self.forward_internal_set(req_data)                

    
    def mainframe(self):

        self.sh_main_layout(massdata=self.massdata)
    
 
        
        