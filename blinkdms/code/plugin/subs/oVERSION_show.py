# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main GUI methods to show parts of a version
File:           oVERSION_show.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
#from blinkdms.code.lib.oDOC import oDOC
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oVERSION import oVERSION_WFL

# from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.gui.form import form
from blinkdms.code.lib.oVERSION import oUPLOADS
from blinkdms.code.lib.oPROJ import oPROJ
from blinkdms.code.lib.oDOC import oD_LINK

class Parts:
    
    def __init__(self, db_obj, _html, objid):
        
        self.objid = objid
        self._html = _html
        
        objlib = oVERSION.Mainobj(self.objid)
        
        self.features = objlib.features(db_obj)
        
        self.doc_id = self.features['vals']['DOC_ID']
        
        self.massdata = {}
        
    def get_doc_id(self):
        return self.doc_id
        
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
        
    def projects_get(self, db_obj):

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
        
    def _uploads_info(self, db_obj, sub_context):
        '''
        :param sub_context: string 
            'ACTIVE'  : the ACTIVE version
            'ARCHIVE' : archive version
        '''

        upload_lib  = oUPLOADS.Mainobj(self.objid)
        upload_list = upload_lib.get_uploads(db_obj)
        
        context='ACTIVE'
        if sub_context=='ARCHIVE':
            context='ARCHIVE'

        upload_infos = {'title': 'Attached files', 'data': [], 'version_id': self.objid, 'edit': 0, 'context':context}
        
        for row in upload_list:
            
            tmp_name = row['NAME']
            doctype='XXX'
            if row['HAS_PDF']:
                doctype='PDF'
                tmp_name = tmp_name + '.pdf'
            
            upload_infos['data'].append( { 'pos':row['POS'], 'name':tmp_name, 'doctype': doctype } )
            
        self.massdata['uploads'] = upload_infos    
        
    def download(self, db_obj, pos, doc_type=''):

       
        doc_lib      = oUPLOADS.Mainobj(self.objid)
        doc_features = doc_lib.features(db_obj, pos)
        
        
        if doc_type=='PDF':
            file_path = doc_lib.file_path_pdf(pos)
            file_nice = doc_features['NAME'] + '.pdf'
        else:
            file_path = doc_lib.file_path(pos)
            file_nice = doc_features['NAME']
        
        
        file_exists = doc_features['file.exists']
        if not file_exists:
            raise BlinkError(1, 'No '+doc_type+ ' file attachment found.')
        
        gui_cont_file =  {
           'filename' : file_path,
           'name' :     file_nice     
        }        
        
        return gui_cont_file
        
        
    
    def audit_log(self, db_obj):
        
        workflow_lib = oVERSION_WFL.Mainobj(db_obj, self.objid)
        wfl_data = workflow_lib.get_aud_log_nice(db_obj)

        wfl_data_table = {'header': {'title': 'Audit log'}, 'data': [], 'cols': []}
        wfl_data_table['cols'] = ['#', 'User', 'Signature date']

        for row in wfl_data:
            wfl_data_table['data'].append([row['POS'], row['USER.name'], row['STATE.name'], row['SIGN_DATE']])
        
        self.massdata['auditlog'] = wfl_data_table
        
    def _links_info(self, db_obj):
        '''
        get DOC links 'doc_links'
        '''
        link_lib  = oD_LINK.Mainobj(self.doc_id)
        link_list = link_lib.get_links_ALL_nice(db_obj)
        
        new_keys = oD_LINK.KEYs_NICE
        
        link_infos = {'title': 'Linked docs', 'context':'ACTIVE', 'data': [], 'version_id': self.objid, 'edit': 0, 'new_keys':new_keys}
        
        new_list = sorted(link_list, key = lambda i: i['KEY']) # sort by KEY
        
        for row in new_list:
            link_infos['data'].append({'v_id': row['VERSION_ID'], 'ch_d_id':row['DOC_ID'], 'nice':row['c.name_all'], 'l.type':row['l.type'] })

        self.massdata['doc_links']= link_infos    
        
    def show_all(self, db_obj, sub_context):
        '''
        :param sub_context: 'ACTIVE, 'ARCHIVE'
        '''
        
        self.projects_get(db_obj)
        
        self.form(self.features)
        
        self._uploads_info(db_obj, sub_context)
        
        self.audit_log(db_obj)
        
        self._links_info(db_obj)

    def get_mass_data(self):
        return self.massdata
    