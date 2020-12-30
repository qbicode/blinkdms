# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
edit a document
File:           doc_edit.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oDOC import oDOC_VERS
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oVERSION import oVERSION_WFL
from blinkdms.code.lib.oVERSION import oVERSION_edit
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.oPROJ import oPROJ
from blinkdms.code.lib.oVERSION import oUPLOADS
from blinkdms.code.lib.oDOC import oD_LINK
from blinkdms.code.lib.gui.form import form
from blinkdms.code.lib.oSTATE import oSTATE
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib import oROLE



class plug_XPL(gPlugin):
    '''
     :var self._req_data:
       'id' : VERSION-ID
       OR 'd_id' DOC_ID
       OR 'cid' : document code 'VA-0002'
       'go' : 0,1
    '''
  
    obj_ext_lib = None  # extender class
    wfl_is_active = 0
    users_review_pr = None  # PLANNED and LOG: AUD_PLAN_pi_STRUCT

    def register(self):

        self.objid = 0
        if 'd_id' in self._req_data:
            doc_id = self._req_data['d_id']
            try:
                doc_id = int(doc_id)
            except:
                doc_id = 0
                
            if doc_id:
                db_obj = self._db_obj1
                doc_vers_lib = oDOC_VERS.Table('EDIT')
                self.objid = doc_vers_lib.get_version_id(db_obj, doc_id)
                
        if 'cid' in self._req_data:
            cid = self._req_data['cid']
            if cid != '':
                db_obj = self._db_obj1
                doc_vers_lib = oDOC_VERS.Table('EDIT')
                self.objid = doc_vers_lib.get_version_by_cid(db_obj, cid) 

        if not self.objid:
            
            idtmp = self._req_data.get('id', 0)
            try:
                self.objid = int(idtmp)
            except:
                self.objid = 0

        self.infoarr['title'] = 'Edit/view document'
        self.infoarr['layout'] = 'doc_edit'
        self.infoarr['viewtype'] = 'object'
        self.infoarr['objtype'] = 'VERSION'
        self.infoarr['id'] = self.objid
        self.infoarr['obj.id_check'] = 1
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT]
        self.infoarr['context.allow'] = ['EDIT']        

    def _init_this(self, db_obj):
        
        self.massdata = {}
        self.form_edit_flag = 0
        self.is_released = 0
        
        self.user_lib = oDB_USER.mainobj(session['sesssec']['user_id'])

        self.vers_lib = oVERSION_edit.Mainobj(db_obj, self.objid)
        self.doc_id = self.vers_lib.doc_id

        if not self.vers_lib.is_current_versid(db_obj):
            raise BlinkError(1, 'This version is not valid for Edit!')

        self._projects_get(db_obj)
    
        features = self.vers_lib.features(db_obj)
        self.features2 = features.copy()
        v_user_id = self.features2['vals'].get('DB_USER_ID', 0)
        if v_user_id:
            v_full_name = oDB_USER.Table.get_fullname(db_obj, v_user_id)
            self.features2['vals']['DB_USER.name'] = v_full_name
        
        if self.vers_lib.is_released(db_obj):
            self.is_released = 1
        

        wfl_active = 0
        if self.vers_lib.workflow_is_active(db_obj):
            wfl_active = 1
        self.wfl_is_active = wfl_active        

        self.workflow_lib = oVERSION_WFL.Mainobj(db_obj, self.objid)
        self.users_review_pr = self.workflow_lib.log_get_plan_versus_is(db_obj)
        

    def form(self, data):

        owner_name =  self.features2['vals'].get('DB_USER.name','')

        fields = [

         {'title': 'Doc + Version', 'edit': 0, 'object': 'text', 'val': data['vals']['C_ID'] + ' v' + str(data['vals']['VERSION'])},
         {'name': 'NAME', 'title': 'Title', 'edit': 1, 'object': 'text', 'required': 1, 'val': data['vals']['NAME']},
         {'name': 'NOTES', 'title': 'Notes', 'edit': 1, 'object': 'textarea', 'required': 0, 'val': data['vals']['NOTES']},
         {'name': 'EXPIRY_DATE', 'title': 'Expiry date', 'edit': 1, 'object': 'text', 'required': 0, 'val': data['vals']['EXPIRY_DATE']},
         {'title': 'Release date', 'edit': 0, 'object': 'text', 'val': data['vals']['RELEASE_DATE']},
         {'title': 'is released and active?', 'edit': 0, 'object': 'text', 'val': data['vals']['IS_ACTIVE']},
         {'title': 'Workflow active?', 'edit': 0, 'object': 'text', 'val': data['vals']['WFL_ACTIVE']},
         {'title': 'Owner', 'edit': 0, 'object': 'text', 'val': owner_name},
        ]
        
        if not self.form_edit_flag:
            # make form not editable
            ind = 0
            for row in fields:
                fields[ind]['edit'] = 0
                ind=ind+1
        
        hidden = {
            "mod":   'doc_edit',
            "action":'update',
            'id':    self.objid,
        }  
        init = {
            'target_id': 'x_set_password'  # it is a modal form ...
        }

        if not self.form_edit_flag:
            init['editmode'] = 'view'

        self.form_obj = form(init, hidden, 0)
        self.form_obj.set_form_defs(fields)
        
        form_data = self.form_obj.get_template_data()
        self.massdata['form'] = form_data
        
    def act_update(self, db_obj, parx):
        

        debug.printx(__name__, "parx:"+  str(parx)  )
        
        params = {
            'vals':  parx
            
        }
        
        act_lib = oVERSION.Modify_obj(db_obj, self.objid)
        act_lib.update(db_obj, params)

        self._html.setMessage('OK', 'Updated.')
        
    def review_info(self, db_obj):

        # state_lib = oSTATE.STATE_info()
        reviewer_table = {'header': {'title': 'Reviewers'}, 'data': [], 'cols': []}
        reviewer_table['cols'] = ['#', 'User', 'Signing date', 'action']

        users_raw = self.users_review_pr.copy()
        
        if not self.wfl_is_active:
            ind = 0
            for row in users_raw:
                users_raw[ind]['date'] = None
                ind = ind + 1


        ind = 0
        for row in users_raw:
            
            datex = None
            user_id = row['DB_USER_ID']
            full_name = oDB_USER.Table.get_fullname(db_obj, user_id)

            datex = row.get('date', None)  # available, if workflow is active
            state_id = row['STATE_ID']
            state_name = oSTATE.STATE_info.get_statekey_by_id(db_obj, state_id)
            
            reviewer_table['data'].append([ind + 1, full_name, datex, state_name])
            ind = ind + 1

        self.massdata['reviewer'] = reviewer_table
        
    def _projects_get(self, db_obj):

        doc_obj_lib = obj_abs('DOC', self.doc_id)
        proj_answer = doc_obj_lib.search_projects(db_obj)

        debug.printx(__name__, "proj_answer:" + str(proj_answer))
        
        if len(proj_answer['proj_arr']):
            proj_id       = proj_answer['proj_id_main']
            proj_lib      = oPROJ.mainobj(proj_id)    
            proj_path_arr = proj_lib.get_path_arr(db_obj)
            self._html.add_meta('proj.path', proj_path_arr)

            if len(proj_answer['proj_arr']) > 1:
                meta_info_tmp = proj_lib.get_proj_arr_names(db_obj, proj_answer['proj_arr'])
                self._html.add_meta('proj.other',  meta_info_tmp  )        

    def _uploads_info(self, db_obj):

        upload_lib = oUPLOADS.Mainobj(self.objid)
        upload_list = upload_lib.get_uploads(db_obj)
        upload_infos = {'title': 'Uploaded docs', 'data': [], 'version_id': self.objid, 'edit': self.form_edit_flag,  'context':'EDIT'}
        
        for row in upload_list:
           
            upload_infos['data'].append( { 'pos': row['POS'], 'name': row['NAME'], 'has_pdf': row['HAS_PDF'], 
                                           'size':row['file.size'], 'mod_date': row['file.mod_date_hum'] } )
        
        self.massdata['uploads'] = upload_infos
        
    def _links_info(self, db_obj):
        '''
        get DOC links
        ''' 
        link_lib  = oD_LINK.Mainobj(self.doc_id)
        link_list = link_lib.get_links_nice(db_obj)
        
        new_keys = oD_LINK.KEYs_NICE
        
        link_infos = {'title': 'Linked docs', 'data': [], 'version_id': self.objid, 'edit': self.form_edit_flag, 'new_keys':new_keys}
        
        for row in link_list:
            link_infos['data'].append({'v_id': row['VERSION_ID'], 'ch_d_id':row['C_DOC_ID'], 'nice':row['c.name_all'], 'l.type':row['l.type'] })

        self.massdata['doc_links']= link_infos

    def _auditlog_info(self, db_obj):
        workflow_lib = oVERSION_WFL.Mainobj(db_obj, self.objid)
        wfl_data = workflow_lib.get_aud_log_nice(db_obj)
        wfl_data_table = {'header': {'title': 'Audit log'}, 'data': [], 'cols': []}
        wfl_data_table['cols'] = ['#', 'User', 'Status', 'Signature date', 'Notes']
    
        for row in wfl_data:
            notes = row['NOTES']
            if notes != None:
                if len(notes) > 150:
                    notes = notes[0:150] + ' ...'
            wfl_data_table['data'].append([row['POS'], row['USER.name'], row['STATE.name'], row['SIGN_DATE'], notes])
        self.massdata['auditlog'] = wfl_data_table
        
   
        
    def startMain(self):
        
        db_obj = self._db_obj1


        self._init_this(db_obj)
        wfl_active = self.wfl_is_active
        

        if 'edit' not in session['sesssec']['roles']:
            raise BlinkError(1, 'This document-tool is only available for users with the "Editor"-Role.')

        self._html.add_meta('doc_id', self.doc_id)

        # admin area
        admin_area_active = 0
        if self.user_lib.has_role(db_obj, oROLE.ROLE_KEY_ADMIN):
            # user is Context-Admin ?
            keyx = 'context.EDIT.admin.active' 
            admin_area_active = session['sesssec'].get(keyx,0)
            self._html.add_meta(keyx, admin_area_active)

        # Admin buttons
        adm_buttons = {
            'reject': 0,
        }

        wfl_buttons = {
            'r_start': 0,
            'r_start.inact': 0,
            'e_start': 0,
            'w_start': 0, # withdraw
            'sign': 0,
            'reject': 0,
            'v_new': 0,
            'v_new.inact': 0,
            'reviewer_edit': 0,
            'upload_docs': 0
        }

        if wfl_active:
            # workflow is active ...
            self.form_edit_flag = 0
            
            plan_dict = self.workflow_lib.user_is_planned_act_reviewer(db_obj) 
            if plan_dict != None:
                wfl_buttons['sign'] = 1
                plan_state_id  = plan_dict['STATE_ID']
                plan_state_key = oSTATE.STATE_info.get_statekey_by_id(db_obj, plan_state_id)
                self._html.add_meta('workflow.sign.state_key', plan_state_key)
                
            if self.vers_lib.is_owner(db_obj):
                wfl_buttons['reject'] = 1
        else:
            if not self.is_released:
                
                if self.vers_lib.is_owner(db_obj):
                    wfl_buttons['v_new.inact'] = 1
                    wfl_buttons['r_start'] = 1
                    wfl_buttons['e_start'] = 1
                    wfl_buttons['w_start'] = 1
                    wfl_buttons['reviewer_edit'] = 1
                    wfl_buttons['upload_docs'] = 1
                    self.form_edit_flag = 1
            else:
                if self.vers_lib.is_owner(db_obj):
                    wfl_buttons['r_start.inact'] = 1
                    wfl_buttons['v_new'] = 1
                    wfl_buttons['w_start'] = 1
   
        self._html.add_meta('workflow.buttons', wfl_buttons)
        
        if admin_area_active:
            
            if wfl_active:
                adm_buttons['reject'] = 1   
                
            self._html.add_meta('admin.buttons', adm_buttons)
        
        self.form(self.features2)
        
        if int(self._req_data.get('go', 0)) > 0:

            parx = self._req_data['parx']
            self.form_obj.check_vals(parx)
            
            self.act_update(db_obj, parx)

            # reload
            self.vers_lib = oVERSION_edit.Mainobj(db_obj, self.objid)
            features = self.vers_lib.features(db_obj)
            self.form(features)


        self._uploads_info(db_obj)
        self._links_info(db_obj)
        self._auditlog_info(db_obj)
        self.review_info(db_obj)


    def mainframe(self):

        self.sh_main_layout(massdata=self.massdata)
    
 
        
        