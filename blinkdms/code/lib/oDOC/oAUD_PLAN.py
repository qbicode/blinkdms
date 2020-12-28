# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
audit plan actions
DB-structure
DOC_ID 	POS 	DB_USER_ID  STATE_ID 	DONE 	PARALLEL 	LAST_EMAIL_DATE 	DAYS_WARN
28 	1 	7 	    5 	        0 			
28 	2 	3 	    5 	        0 			
28 	3 	8 	    6 	        1 			
28 	4 	9 	    6 	        1 		

File:           oDOC/oAUD_PLAN.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from flask import request

from blinkdms.code.lib.main_imports import *
from ..obj_mod import Obj_mod
from blinkdms.code.lib.f_mail import MailMain
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.oSTATE import oSTATE


REV_TYPE_REVIEW ='REVIEW'
REV_TYPE_RELEASE='RELEASE' #last part of the release workflow
REV_TYPE_EDIT   ='EDIT' # EDIT workflow

class Table:
    """
    general table methods, static ?
    """
    def __init__(self):
        pass
    
    @staticmethod
    def get_state_id_by_revtype(db_obj, rev_type):
        
        state_key='?'
        if rev_type==REV_TYPE_REVIEW:
            state_key='REVIEW'
        if rev_type==REV_TYPE_RELEASE:
            state_key='REVIEW_REL'        

        state_id = oSTATE.STATE_info.get_stateid_by_key(db_obj, state_key)
        return state_id
    
class Modify_obj(Obj_mod):
    """
    modify an object
    """
    
    def __init__(self, db_obj, objid=None):
        super().__init__(db_obj, 'DOC', objid)
        
    def _send_emails(self, db_obj, state_id, db_user_ids):
        # send emails an review users ...
        # TBD send emails to users ...
        # TBD: get DOC.CID
        #
        
        libx = MailMain()

        meta_content = {}
        mail_tmpl_file = 'email/doc_status_email.html'  # TBD create this

        obj_lib = obj_abs('DOC', self.objid)
        doc_code = obj_lib.main_feat_val(db_obj, 'C_ID')
        
        base_url = request.base_url
        doc_url = base_url + '?mod=doc_edit&cid=' + doc_code
        
        for user_id_loop in db_user_ids:
            # get full name, email
            userlib = oDB_USER.mainobj(user_id_loop)
            user_feats = userlib.features(db_obj)

            fullname = user_feats['FULL_NAME']
            emailaddr = user_feats['EMAIL']
            if emailaddr == '' or emailaddr == None:
                # TBD log error, ignore ...
                error = 1
                continue

            meta_content['doc.cid'] = doc_code
            meta_content['doc.url'] = doc_url
            subject = 'DMS: Review doc ' + doc_code
            
            libx.send_mail(emailaddr, fullname, subject, meta_content, mail_tmpl_file)
        
        
    def _update_status_all(self, db_obj, rev_type, status):
        '''
        TBD: what is if state_id_expect is not planned ???
        
        - update AUD_PLAN.DONE flag for selected users by rev_type
        - send emails !
        :param rev_type: string 
           REVIEW,  - first part of the release workflow;
                      if no REVIEW planned, switch immediatly to RELEASE
           RELEASE, - last part of the release workflow
           EDIT     - edit workflow
           ALL      - update all !
        :param status: int 
            0: nix
            1: pleased to review
            2: done
        '''
        
        state_id_expect = 0
        if rev_type!='ALL': 
            state_id_expect = Table.get_state_id_by_revtype(db_obj, rev_type)
    
        # collect all planned entries
        plan_pos_arr = []
        sql_cmd = 'POS, DB_USER_ID, STATE_ID from AUD_PLAN where DOC_ID=' + str(self.objid) + ' order by POS'
        db_obj.select_dict(sql_cmd)
        while db_obj.ReadRow():
            plan_pos_arr.append(db_obj.RowData)
            
        
        # update the relevant entries (the relevant STATE_ID)
        db_user_ids = []
       
        for row in plan_pos_arr:
            
            pos          = row['POS']
            loop_user_id = row['DB_USER_ID']
            state_id_loop= row['STATE_ID']
            
            if rev_type=='ALL' or state_id_expect == state_id_loop:
                
                args = {'DONE': status}
                db_user_ids.append(loop_user_id)
                db_obj.update_row('AUD_PLAN', {'DOC_ID': self.objid, 'POS': pos}, args)
            
        return {'state_id': state_id_expect, 'users': db_user_ids}
        

    def review_start(self, db_obj, rev_type, status):
        '''
        start review process for all relevant users
        :param rev_type: string
        '''
        status = 1
        result = self._update_status_all(db_obj, rev_type, status)
        
        # TBD: ignore exception here ....
        self._send_emails(db_obj, result['state_id'], result['users'])

    def review_stop(self, db_obj, rev_type):
        '''
        start review process for all users
        '''
        self._update_status_all(db_obj, rev_type, 0)
        
    def review_stop_all(self, db_obj):
        '''
        start review process for all users
        '''
        status = 0
        self._update_status_all(db_obj, 'ALL', status)    

    def user_did_review(self, db_obj, state_id):
        '''
        this user did review/release or other
        '''
        pos = 0
        sql_cmd = 'POS from AUD_PLAN where DOC_ID=' + str(self.objid) + ' and DB_USER_ID=' + str( session['sesssec']['user_id'])
        db_obj.select_tuple(sql_cmd)
        if db_obj.ReadRow():
            pos = db_obj.RowData[0]

        if not pos:
            return
        
        status = 2
        args = {'DONE': status}
        db_obj.update_row('AUD_PLAN', {'DOC_ID': self.objid, 'POS': pos}, args)