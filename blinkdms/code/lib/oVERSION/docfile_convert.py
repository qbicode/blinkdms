# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"


import tempfile
import os

#from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.f_utilities import BlinkError
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib import f_workdir
from blinkdms.code.lib import f_date

from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.oVERSION import oVERSION_edit, oVERSION_WFL
from blinkdms.code.lib.oVERSION import oUPLOADS
from blinkdms.code.lib.fOffice.ms_text_replace import MS_text_replace, MS_sub_object
from blinkdms.code.lib.fOffice.ms_2_pdf import MS_2_pdf
"""
replace text in version document
File:           docfile_convert.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""




class DocReplaceText:
    
    filename = ''
    
    
    def __init__(self, db_obj, filename):
        self.filename = filename
        self.convert_errors=[]

        
    def set_file(self,filename):
        '''
        can be set separatly
        '''
        self.filename = filename
        
    def convert(self, replace_dict):
        '''
        replace text in word document
        - this method can be called without saving the file ...
        :param replace_dict
        'header': {'Title', 'Code', ...}
        'review': [   list of reviewers
           { F,N,S,D }
        ] 
        '''
        
        if self.filename=='':
            raise BlinkError(1, 'No filename set.')
        
        self.convert_errors=[]
        
        self.doc_lib = MS_text_replace(self.filename)
        pos_key   = '{{SOP-R-F}}'
        table_row_COORD = self.doc_lib.table_find_row(pos_key, 0)
        if not table_row_COORD:
            raise BlinkError(2, 'Pattern "' +pos_key+  '" not found in document.')
        
        #
        # review
        #
        if 'review' not in replace_dict:
            raise BlinkError(3, 'Review dict missing.')        
        
        head_keys = ['F', 'N', 'S', 'D']
       
        i = 0
        for review_row in replace_dict['review']:
            
            replace_list=[]
            for key in head_keys:
                if key not in review_row:
                    raise BlinkError(4, 'Value for key '+key+' missing.')  
                replace_list.append( { 'old': '{{SOP-R-'+key+'}}', 'new': review_row[key] } )        
            
            #replace_list = [
                #{ 'old': '{{SOP-R-F}}', 'new': 'Author' },
                #{ 'old': '{{SOP-R-N}}', 'new': 'St. Kube' },
                #{ 'old': '{{SOP-R-S}}', 'new': '' },
                #{ 'old': '{{SOP-R-D}}', 'new': '2020-08-09' },
            #]   
            
            if not i:
                
                row_poi = table_row_COORD['content_row_poi']
                self.doc_lib.update_cells(row_poi, replace_list)
            else:
                row_poi = self.doc_lib.table_add_row(table_row_COORD)
                self.doc_lib.update_cells(row_poi, replace_list)
                
            i = i + 1
            
        #
        # header
        #
        if 'header' not in replace_dict:
            raise BlinkError(3, 'Header dict missing.')
        
        head_keys = ['Title', 'Code', 'Version', 'Valid', 'Docstate' ]
       
        replace_list=[]
        for key in head_keys:
            if key not in replace_dict['header']:
                raise BlinkError(5, 'Header: Value for key '+key+' missing.')   #+
            val = replace_dict['header'][key]
            replace_list.append( { 'old': '{{SOP-'+key+'}}', 'new': val } )
              
        
        header_tab = self.doc_lib.get_header_table()
        doc_sub2_obj_lib = MS_sub_object(header_tab)
        doc_sub2_obj_lib.table_find_replace_many(replace_list)
        warnings = doc_sub2_obj_lib.get_warnings()
        
        if len(warnings):
            raise BlinkError(1, 'Replacement warnings: '+str(warnings) ) 
        
    def save(self,filename=''):
        
        self.doc_lib.save(filename)  
        
class Doc2Pdf:
    '''
    first replace text in word file, than convert to PDF
    
    '''
    
    filename = ''
    objid    = None
    pos      = None
    upload_row = None # dict of UPLOAD row
    
    def __init__(self, db_obj, version_id):
        self.objid    = version_id
        self.filename = ''
        
        if version_id:
            self.get_file_from_version(db_obj)
            
    def get_dyna_content(self, db_obj, preview_flag=0):
        '''
        :param preview_flag: 0,1 create a preview ???
        '''
        
        doc_lib  = oVERSION_edit.Mainobj(db_obj, self.objid)
        features = doc_lib.features(db_obj)
        
        version_info_lib = oVERSION_WFL.Mainobj(db_obj, self.objid)
        aud_log_list     = version_info_lib.get_aud_log_last_release(db_obj)
        version_info_lib.aud_log_trans_nice(db_obj, aud_log_list)
        
        date_head_out = '?'
        doc_state='PREVIEW'
        if not preview_flag:
            if features['vals']['VALID_DATE'] is None:
                raise BlinkError(1,'VALID_DATE is missing.')
            
            date_head_out = f_date.f_datetime2YMD( features['vals']['VALID_DATE'] )
            doc_state='Freigegeben'
        
        header = {
            'Title':   features['vals']['NAME'],
            'Code':    features['vals']['C_ID'], 
            'Version': str(features['vals']['VERSION']),
            'Valid':    date_head_out  ,
            'Docstate': doc_state
        } 
        
        head_keys = [
            { 'src': 'extra'    , 'dst':'F' },
            { 'src': 'USER.name', 'dst':'N' },
            { 'src': 'extra', 'dst':'S' },
            { 'src': 'SIGN_DATE'  , 'dst':'D' },
        ]
        
        review_list = []
        
        #
        # add AUTHOR row
        #
        user_id   = features['vals']['DB_USER_ID']
        user_lib  = oDB_USER.mainobj(user_id)
        user_name = user_lib.get_fullname(db_obj)        

        editor_row = {
            'F':'Author',
            'N': user_name,
            'S': 'N/A',
            'D': 'N/A'
        }
        review_list.append(editor_row) 
        
        #
        # add other reviewers
        #        
        for review_row in aud_log_list:
            
            one_reviewer_out={}
            add_to_log = 0
            
            for key_row in head_keys:

                dest_key = key_row['dst']
                    
                if dest_key=='F':
                    state_key = review_row['STATE.key']
                    
                    while 1:
                        val = '?'
                        if state_key=='REVIEW':
                            val='Reviewer'
                            add_to_log = 1
                            break
                        if state_key=='REVIEW_REL':
                            val='Releaser' 
                            add_to_log = 1
                            break
                        
                        add_to_log = 0 # ignore this review row ...
                        break          # final break
                        
                if dest_key== 'S':
                    val = 'electronically signed'  
                    
                if dest_key=='N':
                    val = review_row['USER.name']
                    
                if dest_key=='D':
                    val_tmp = review_row['SIGN_DATE'] 
                    val = f_date.f_datetime2YMD(val_tmp)
                    
                one_reviewer_out[key_row['dst']] = val
        
            if add_to_log:
                review_list.append(one_reviewer_out)    
        
        replace_dict = {
            'header':header,
            'review': review_list
        }
        
        return replace_dict
            
    def get_file_from_version(self, db_obj):
        '''
        get the filename
        - check, if UPLOAD entry exists, gets filename
        - do not do extensible checks here ...
        '''
        self.filename = ''
        self.upload_lib  = oUPLOADS.Mainobj(self.objid)
        upload_list = self.upload_lib.get_uploads(db_obj)
        
        if not upload_list:
            raise BlinkError(1, 'No Attachment found on document.')
        
        first_elem    = upload_list[0]
        self.pos      = first_elem['POS']
        self.filename = self.upload_lib.file_path(self.pos) 
        self.upload_row = first_elem
        
    
    def check(self, db_obj):
        '''
        extended checks
        '''
        if not os.path.exists(self.filename):
            raise BlinkError(1, 'Attachment not found on server.') 

        if not os.path.getsize(self.filename):
            raise BlinkError(1, 'Attachment is empty.') 

        # analyse extension
        file_nice_name = self.upload_row['NAME']
        file_name, file_extension = os.path.splitext(file_nice_name)
        if file_extension!='.docx':
            raise BlinkError(2, 'Attachment is not of type "docx".')   
        
    def check_document(self, db_obj):
        '''
        just check the document for conversion, no saving of file ...
        '''
        self.check(db_obj)

        preview_flag = 1
        replace_dict = self.get_dyna_content(db_obj, preview_flag)
        
        word_replace_lib = DocReplaceText(db_obj, 0)
        word_replace_lib.set_file(self.filename)
        word_replace_lib.convert(replace_dict)
        
    def convert(self, db_obj, preview_flag=0):
        '''
        convert DOCX to PDF
        '''
        
        debug.printx(__name__, "do_PDF_Convert of document: VERSION_ID: "+str(self.objid) )
        
        self.check(db_obj)
        
        worktmp = f_workdir.main()
        workdir = worktmp.getWorkDir('.') 
        
        replace_dict = self.get_dyna_content(db_obj, preview_flag)
        
        word_replace_lib = DocReplaceText(db_obj, 0)
        word_replace_lib.set_file(self.filename)
        word_replace_lib.convert(replace_dict)
   
        
        tmpfile_short = next(tempfile._get_candidate_names()) + '.docx' # append docx because the PDF converter needs a file extension ..     
        file_word_tmp = os.path.join(workdir, tmpfile_short)
        word_replace_lib.save(file_word_tmp)
        
        outfile = self.upload_lib.file_path_pdf(self.pos)
        
        word_pdf_lib = MS_2_pdf()
        word_pdf_lib.convert_to_pdf(file_word_tmp, outfile)
        
        if not preview_flag:
            upload_mod_lib = oUPLOADS.Modify_obj(db_obj, self.objid)
            upload_mod_lib.set_pos(self.pos)
            pdf_flag = 1
            upload_mod_lib.set_pdf_flag(db_obj, pdf_flag)
            
     
        
if __name__ == "__main__":
    
    filename    =r'C:\Users\Steffen\Documents\Code\blinkdms\test\blinkdms\code\lib\oVERSION\Vorlage_SOP_t1.docx'
    filename_new=r'C:\Users\Steffen\Documents\Code\blinkdms\test\blinkdms\code\lib\oVERSION\Vorlage_SOP_t1.tr.docx'
    version_id=0
    
    db_obj    =None
    a = DocReplaceText(db_obj, version_id)
    a.set_file(filename)
    replace_list= []
    a.convert(replace_list)
    a.save(filename_new)
    
    b = Doc2Pdf(db_obj, version_id)
    b.convert()