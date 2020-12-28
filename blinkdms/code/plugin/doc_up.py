# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
document FILE actions in EDIT area
File:           doc_up.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from werkzeug.utils import secure_filename

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oVERSION import oUPLOADS
#from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.oVERSION import oVERSION_edit
from blinkdms.code.lib.gui.form import form
from blinkdms.code.lib import oROLE
from blinkdms.code.lib.oDOC_TYPE import oDOC_TYPE



class plug_XPL(gPlugin):
    '''
     :var self._req_data:
       'id' : VERSION-ID
       'go' : 0,1  
       'pos' : POS on update
       'act':
         'new'    upload new file
         'upload' FUTURE: only update/upload a new attachment, need 'pos', VERSION is in EDIT
         'down'   download, need 'pos'
         'del'    delete
        
        'type' = [DEF], 'PDF' for pdf file
         
    '''
  
    obj_ext_lib  = None # extender class

    def register(self):

        idtmp = self._req_data.get('id', 0)
        try:
            self.objid = int(idtmp)
        except:
            self.objid = 0

        self.infoarr['title'] = 'Document file actions'
        self.infoarr['layout'] = 'doc_up'
        self.infoarr['viewtype'] = 'object'
        self.infoarr['objtype'] = 'VERSION'
        self.infoarr['id'] = self.objid
        self.infoarr['obj.id_check'] = 1
        self.infoarr['locrow.show_mo']=1
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT]
        
        act = self._req_data.get('act', '')
        
        
        
        self.infoarr['context.allow'] = ['EDIT']        

    def _do_upload(self, db_obj, file_obj):
        '''
        create NEW upload entry
        '''
        file_short  = secure_filename(file_obj.filename)
        objlib      = obj_abs('DOC', self.doc_id)
        doc_type_id = objlib.main_feat_val(db_obj, 'DOC_TYPE_ID')
        
        doctype_lib = oDOC_TYPE.Mainobj(doc_type_id)
        word_convert_flag = doctype_lib.get_word_convert_flag(db_obj)        
        doc_lib     = oUPLOADS.Mainobj(self.objid)
         
        # analyse existing uploads
        if word_convert_flag:
           
            if doc_lib.has_doc_file(db_obj):
                raise BlinkError(1, 'This doc type has a PDF-conversion. A word file already exists.')
        
        # check if doc already exists
        already_exists = doc_lib.file_exists_in_uploads(db_obj, file_short)
        if len(already_exists):
            raise BlinkError(2, 'This filename already exists on your uploads..')


        modlib = oUPLOADS.Modify_obj(db_obj, self.objid)

        params_use = {
            'NAME': file_short
        }
        
        pos = modlib.new(db_obj, params_use)
        modlib.set_pos(pos)
        
        dest_file_path = modlib.file_path()
        file_obj.save(dest_file_path)
            
        self.setMessage('OK', 'Doc Uploaded Pos:' + str(pos))
        
        return pos
    
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

    def _delete_form(self):
        
        hidden = {
            "mod": self._mod,      
        }       
        
        hidden =  {
            "mod":  self._mod,   
            'act': 'del',
            'id' : self.objid,
            'pos': self.pos
        }
        form_obj = form( { 
            'title':'Delete this attachment?',
            "submittitle":'Delete',
            'editmode': 'edit' 
            }, hidden, 0)
        
        self.massdata['form'] = form_obj.get_template_data()
                 

    def _delete(self, db_obj):
        
        modlib = oUPLOADS.Modify_obj(db_obj, self.objid)
        modlib.set_pos(self.pos)
        modlib.delete_up(db_obj)
        self.setMessage('OK', 'Doc attachment  at pos:' + str(self.pos)+' deleted.')
    
    def startMain(self):

        db_obj = self._db_obj1
        
        self.massdata = {'form': {}}
        self._html.add_meta('id', self.objid)

        objlib = oVERSION_edit.Mainobj(db_obj, self.objid)
        self.doc_id = objlib.get_docs_id()
        
        parx = self._req_data.get('parx', {})
        go = int(self._req_data.get('go', '0'))
        action = self._req_data.get('act', '')     
        self._html.add_meta('act', action)
        
        if action not in ['new', 'upload', 'del', 'down']:
            raise BlinkError(1, 'Action '+action+' unknown.')        
       
        if not objlib.get_current_versid(db_obj):
            raise BlinkError(2, 'This version is not valid for Edit-Mode!')

        if action in ['new', 'upload', 'del']:
            
            if objlib.workflow_is_active(db_obj):
                raise BlinkError(3, 'A workflow is active.')

        
        
        pos = int(self._req_data.get('pos', '0'))
        self.pos = pos
        
        if action != 'new':
            if not self.pos:
                raise BlinkError(4, 'Input: pos missing.')            
        
        if action == 'down':
            if not self.pos:
                raise BlinkError(5, 'Input: pos missing.')              
            self._download(db_obj)
            return
        
        if action == 'del':
            
            if not self.pos:
                raise BlinkError(6, 'Input: pos missing.')              
            
            if go > 0:      
                self._delete(db_obj)
                return
            else:
                self._delete_form()
                
        if action == 'upload':
            
            if not self.pos:
                raise BlinkError(7, 'Input: pos missing.')              
            
            # TBD
            self.setMessage('WARN', 'Upload method not yet implemented.')
            if go > 0:      
                return
            else:
                pass        

        if action == 'new' and go > 0:
            
            #values_new = self._req_data.get('argu', {})

            if '__FILES__' not in self._req_data:
                raise BlinkError(10, 'Please select a file.')
            
            if 'y.file' not in self._req_data['__FILES__']:
                raise BlinkError(11, 'Please select a file.')            
                
            file_obj   = self._req_data['__FILES__']['y.file']

            self._do_upload(db_obj, file_obj)

            self._html.setMessage('OK', 'ok')
            req_data = {
                'mod': 'doc_edit',
                'id': self.objid
                 }
            self.forward_internal_set(req_data)
            
        else:
            # self.form_sign(parx)
            pass

    
    def mainframe(self):

        self.sh_main_layout(massdata=self.massdata)
    
 
        
        