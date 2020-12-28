# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
view a document
File:           doc_view.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oDOC import oDOC
from blinkdms.code.lib.oDOC import oDOC_VERS
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oVERSION import oVERSION_WFL
from blinkdms.code.lib.oVERSION import oVERSION_edit
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.gui.form import form
from blinkdms.code.lib.oVERSION import oUPLOADS
from blinkdms.code.lib.oPROJ import oPROJ
from blinkdms.code.lib import oROLE



class plug_XPL(gPlugin):
    '''
     :var self._req_data:
       'id' : VERSION-ID
       'd_id' doc_ID
       'act'
          'down' : needs 'pos'
       'pos' : INT pos of download doc
    '''
  
    obj_ext_lib  = None # extender class

    def register(self):

        self.objid = 0
        do_check_id = 1
        self.err_of_register = None
        
        if 'd_id' in self._req_data:
            doc_id = self._req_data['d_id']
            try:
                doc_id = int(doc_id)
            except:
                doc_id = 0
            if doc_id:
                db_obj = self._db_obj1
                doc_vers_lib = oDOC_VERS.Table('ACTIVE')
                self.objid = doc_vers_lib.get_version_id(db_obj, doc_id)
                if not self.objid:
                    self.err_of_register = {
                        'doc_id':doc_id 
                    }
                    do_check_id = 0

                
        if not self.objid:
            
            idtmp = self._req_data.get('id', 0)
            try:
                self.objid = int(idtmp)
            except:
                self.objid = 0        

        self.infoarr['title'] = 'view document'
        self.infoarr['layout'] = 'doc_view'
        self.infoarr['objtype'] = 'VERSION'
        
        if do_check_id:
            self.infoarr['viewtype'] = 'object'
            self.infoarr['id'] = self.objid
            self.infoarr['obj.id_check'] = 1
        else:
            self.infoarr['viewtype'] = 'tool'
            
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT, oROLE.ROLE_KEY_VIEW]
        self.infoarr['context.allow'] = ['ACTIVE']        

    def form(self, data):
        

        fields = [

         {'title': 'Doc + Version', 'edit': 0, 'object': 'text', 'val': data['vals']['C_ID'] + ' v' + str(data['vals']['VERSION'])},
         {'name': 'NAME', 'title': 'Title', 'edit': 1, 'object': 'text', 'required': 1, 'val': data['vals']['NAME']},
         {'name': 'NOTES', 'title': 'Notes', 'edit': 1, 'object': 'textarea', 'required': 0, 'val': data['vals']['NOTES']},
         {'name': 'EXPIRY_DATE', 'title': 'Expiry date', 'edit': 1, 'object': 'text', 'required': 0, 'val': data['vals']['EXPIRY_DATE']},
         {'title': 'Release date', 'edit': 0, 'object': 'text', 'val': data['vals']['RELEASE_DATE']},
         {'title': 'is released and active?', 'edit': 0, 'object': 'text', 'val': data['vals']['IS_ACTIVE']},
         {'title': 'Workflow active?', 'edit': 0, 'object': 'text', 'val': data['vals']['WFL_ACTIVE']},
        ]
        

        # make form not editable
        ind = 0
        for row in fields:
            fields[ind]['edit'] = 0
            ind=ind+1
        
        hidden = {
            "mod": 'doc_edit',

            'id': self.objid,
        }
        init = {
            'target_id': 'x_set_password'  # it is a modal form ...
        }


        init['editmode'] = 'view'

        self.form_obj = form(init, hidden, 0)
        self.form_obj.set_form_defs(fields)
        
        form_data = self.form_obj.get_template_data()
        self.massdata['form'] = form_data
        
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

        upload_infos = {'title': 'Attached files', 'data': [], 'version_id': self.objid, 'edit': 0, 'context':'ACTIVE'}
        
        for row in upload_list:
            
            tmp_name = row['NAME']
            doctype='XXX'
            if row['HAS_PDF']:
                doctype='PDF'
                tmp_name = tmp_name + '.pdf'
            
            upload_infos['data'].append( { 'pos':row['POS'], 'name':tmp_name, 'doctype': doctype } )
            
        self.massdata['uploads'] = upload_infos    
        
    def _download(self, db_obj):

        pos          = self.pos
        doc_lib      = oUPLOADS.Mainobj(self.objid)
        doc_features = doc_lib.features(db_obj, pos)
        
        f_type = self._req_data.get('type', '')
        if f_type=='PDF':
            file_path = doc_lib.file_path_pdf(pos)
            file_nice = doc_features['NAME'] + '.pdf'
        else:
            file_path = doc_lib.file_path(pos)
            file_nice = doc_features['NAME']
        
        
        file_exists = doc_features['file.exists']
        if not file_exists:
            raise BlinkError(1, 'No '+f_type+ ' file attachment found.')
        
        self.infoarr['gui'] = -1  # for download
        self.infoarr['gui.cont.type'] ='file'
        self.infoarr['gui.cont.file'] = {
           'filename' : file_path,
           'name' :     file_nice     
        }        
    
        
    def review_info(self, db_obj, objlib):
        
        
        reviewer_table = {'header': {'title': 'Reviewers'}, 'data': [], 'cols': []}
        reviewer_table['cols'] = ['#', 'User']


        users_raw = objlib.get_review_users(db_obj)

        ind = 0
        for row in users_raw:

            user_id = row['DB_USER_ID']
            full_name = oDB_USER.Table.get_fullname(db_obj, user_id)
            reviewer_table['data'].append([ind + 1, full_name])
            ind = ind + 1

        self.massdata['reviewer'] = reviewer_table    

    def startMain(self):
        
        db_obj = self._db_obj1
        
        self.massdata = {}
        self.is_released = 0
        action = self._req_data.get('act', '')   
        pos    = int(self._req_data.get('pos', '0'))
        self.pos = pos        

        if self.err_of_register != None:
            doc_id = self.err_of_register['doc_id']
            doc_obj = obj_abs('DOC', doc_id)
            if not doc_obj.obj_exists(db_obj):
                raise BlinkError(1, 'Document with internal-ID ' + str(doc_id) + ' is unknown.')
            nicename = doc_obj.obj_nice_name(db_obj)
            raise BlinkError(2, 'Document "' + nicename + '" has no valid version.')            


        objlib = oVERSION_edit.Mainobj(db_obj, self.objid)
        self.doc_id = objlib.doc_id

        if not objlib.get_current_versid(db_obj):
            raise BlinkError(1, 'This version is not valid for Edit!')
        
        
        if action == 'down':
            if not self.pos:
                raise BlinkError(1, 'Input: pos missing.')              
            self._download(db_obj)
            return        
        
            
        features = objlib.features(db_obj)
        
        if objlib.is_released(db_obj):
            self.is_released = 1

        self._projects_get(db_obj)
        self.form(features)
        
        self._uploads_info(db_obj)

        workflow_lib = oVERSION_WFL.Mainobj(db_obj, self.objid)
        wfl_data = workflow_lib.get_aud_log_nice(db_obj)

        wfl_data_table = {'header': {'title': 'Audit log'}, 'data': [], 'cols': []}
        wfl_data_table['cols'] = ['#', 'User', 'Signature date']

        for row in wfl_data:
            wfl_data_table['data'].append([row['POS'], row['USER.name'], row['STATE.name'], row['SIGN_DATE']])
        
        self.massdata['auditlog'] = wfl_data_table

        self.review_info(db_obj, objlib)
        
    
    def mainframe(self):

        self.sh_main_layout(massdata=self.massdata)
    
 
        
        