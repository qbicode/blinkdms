# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main DOC sub methods
File:           oVERSION_WFL.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>

:var AUD_LOG_nice_Struct list of dict {}
   POS 	
   DB_USER_ID 
   USER.name  : full name of user
   SIGN_DATE 	
   STATE_ID 
   STATE.name : nice name of state
   STATE.key  : key of state
   NOTES
"""
from datetime import datetime

from blinkdms.code.lib.main_imports import *
from ..obj_mod import Obj_assoc_mod, Obj_mod
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.oSTATE import oSTATE
from blinkdms.code.lib.oDOC import oAUD_PLAN
from blinkdms.code.lib.oVERSION import oVERSION_edit
from blinkdms.code.lib.oVERSION import oUPLOADS
from blinkdms.code.lib.oDOC_TYPE import oDOC_TYPE
from blinkdms.code.lib.oWFL import oWFL

from blinkdms.code.lib.oVERSION.docfile_convert import  Doc2Pdf



class Mainobj:
    __id   = None
    obj    = None # lib obj_abs()
    doc_id = None
    rw_type = None # REV_TYPE_WITHDRAW or REV_TYPE_RELEASE
    
    def __init__(self, db_obj, idx):
        self.__id = idx
        self.obj  = obj_abs('VERSION', idx)
        self.doc_id = self.obj.main_feat_val(db_obj, 'DOC_ID')
        
        #self.state_lib = oSTATE.STATE_info()
    
    
        
    def features(self, db_obj):
        return self.obj.main_feat_all(db_obj)
    
    def get_doc_type_key(self, db_obj):
        '''
        get WFL:KEYX
        '''
        
        objlib      = obj_abs('DOC', self.doc_id)
        doc_type_id = objlib.main_feat_val(db_obj, 'DOC_TYPE_ID')
        doctype_lib = oDOC_TYPE.Mainobj(doc_type_id)
        wfl_type = doctype_lib.get_wfl_type_key(db_obj)
        return wfl_type
        
    def get_def_WORD_CONVERT(self, db_obj):
        '''
        attachment has to be converted to PDF ?
        :return: int 0 or 1
        '''
        
        objlib      = obj_abs('DOC', self.doc_id)
        doc_type_id = objlib.main_feat_val(db_obj, 'DOC_TYPE_ID')
        
        doctype_lib = oDOC_TYPE.Mainobj(doc_type_id)
        word_convert_flag = doctype_lib.get_word_convert_flag(db_obj)
        
        return word_convert_flag

    def get_state_id_from_key(self, db_obj, key):
        return oSTATE.STATE_info.get_stateid_by_key(db_obj, key)

    def get_aud_log(self, db_obj):
        
        sql_cmd = "* from AUD_LOG where VERSION_ID=" + str(self.__id) + " order by POS"
        db_obj.select_dict(sql_cmd)
            
        all_data = []
        while db_obj.ReadRow():
            all_data.append(db_obj.RowData)

        return all_data

    def get_aud_pos_last_STATE(self, db_obj, start_id):

        sql_cmd = "max(POS) from AUD_LOG where VERSION_ID=" + str(self.__id) + " and STATE_ID=" + str(start_id)
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        pos = db_obj.RowData[0]

        return pos

    def get_aud_pos_last_release(self, db_obj):

        start_id =  oSTATE.STATE_info.get_stateid_by_key(db_obj, 'REL_START')
        return self.get_aud_pos_last_STATE(db_obj, start_id)
    
    def get_aud_log_last_release(self, db_obj):
        '''
        get all entries of last RELEASE(START): only REVIEW + APPROVE + REVIEW_REL + RELEASE; No rejects
        '''

        start_pos = self.get_aud_pos_last_release(db_obj)
        if not start_pos:
            #raise BlinkError(1, "No Release-Start found.")
            return []

        allow_states = [
            oSTATE.STATE_info.get_stateid_by_key(db_obj, 'REVIEW'),
            oSTATE.STATE_info.get_stateid_by_key(db_obj, 'REVIEW_REL'),
            oSTATE.STATE_info.get_stateid_by_key(db_obj, 'REL_END'),
        ]

        sql_cmd = "* from AUD_LOG where VERSION_ID=" + str(self.__id) + " and POS>=" + str(start_pos) + " order by POS"
        db_obj.select_dict(sql_cmd)
  
        all_data = []
        while db_obj.ReadRow():
            loop_state_id = db_obj.RowData['STATE_ID']
            if loop_state_id in allow_states:
                all_data.append(db_obj.RowData)

        return all_data
    
    def get_aud_log_last_withdraw(self, db_obj):
        '''
        get all entries of last WD(START): only REVIEW + APPROVE + REVIEW_WD + WD; No rejects
        '''

        start_id =  oSTATE.STATE_info.get_stateid_by_key(db_obj, 'WD_START')
        start_pos = self.get_aud_pos_last_STATE(db_obj, start_id)
        if not start_pos:
            #raise BlinkError(1, "No WD-Start found.")
            return []

        allow_states = [
            oSTATE.STATE_info.get_stateid_by_key(db_obj, 'REVIEW'),
            oSTATE.STATE_info.get_stateid_by_key(db_obj, 'REVIEW_WD'),
            oSTATE.STATE_info.get_stateid_by_key(db_obj, 'WD_END'),
        ]

        sql_cmd = "* from AUD_LOG where VERSION_ID=" + str(self.__id) + " and POS>=" + str(start_pos) + " order by POS"
        db_obj.select_dict(sql_cmd)
  
        all_data = []
        while db_obj.ReadRow():
            loop_state_id = db_obj.RowData['STATE_ID']
            if loop_state_id in allow_states:
                all_data.append(db_obj.RowData)

        return all_data    

    def check_start_r_wfl(self, db_obj):
        a = Check_Wfl_Start(self.__id)
        answer = a.check(db_obj)
        return answer
    
    def get_aud_log_nice(self, db_obj):
        '''
        :return: list  AUD_LOG_nice_Struct
        '''
        last_user_id = 0
        all_states = oSTATE.STATE_info.get_all_by_id(db_obj)

        raw_data = self.get_aud_log(db_obj)
        ind = 0
        for row in raw_data:

            user_id = row['DB_USER_ID']
            if last_user_id != user_id:
                user_lib = oDB_USER.mainobj(user_id)
                user_name = user_lib.get_fullname(db_obj)
            
            raw_data[ind]['USER.name'] = user_name

            state_id = row['STATE_ID']
            state_inf_row = all_states.get(state_id, {})
            state_nice = state_inf_row.get('NICE', '?')
            
            raw_data[ind]['STATE.name'] = state_nice
            
            ind = ind + 1
            last_user_id = user_id
            

        return raw_data
    
    def get_wf_plan(self, db_obj):
        doc_obj  = obj_abs('DOC', self.doc_id)
        wf_plan = doc_obj.main_feat_val(db_obj, 'WF_PLAN')
        return wf_plan

    def log_get_plan_versus_is(self, db_obj):
        '''
        get list: PLANNED reviews == reviews in audit log
        :return: AUD_PLAN_pi_STRUCT : list of {POS,  DB_USER_ID, STATE_ID, DONE, PARALLEL, 'found', 'datex'}
        '''
        obj_ed_lib = oVERSION_edit.Mainobj(db_obj, self.__id)
        #  {POS,  DB_USER_ID, STATE_ID, DONE, PARALLEL }
        planned_users = obj_ed_lib.get_review_users(db_obj)
        if not len(planned_users):
            #raise BlinkError(1, 'No Planned Users found.')
            return []

        wf_plan = self.get_wf_plan(db_obj)
        rw_type = oAUD_PLAN.REV_PLAN_REV_DICT.get(wf_plan,'')

        if rw_type == oAUD_PLAN.REV_TYPE_WITHDRAW:
            log_arr = self.get_aud_log_last_withdraw(db_obj)
        else:
            log_arr = self.get_aud_log_last_release(db_obj)

        out_list = []
        for row in planned_users:
            
            row_tmp = row.copy()
            plan_state_id = row['STATE_ID']
            user_id       = row['DB_USER_ID']

            loop_entry_found = 0
            datex = None
            for log_row in log_arr:
                if log_row['DB_USER_ID'] == user_id and log_row['STATE_ID'] == plan_state_id:
                    loop_entry_found = 1
                    datex = log_row['SIGN_DATE']
                    break
                
            

            row_tmp['found'] = loop_entry_found
            row_tmp['date'] = datex

            out_list.append(row_tmp)
            
        return out_list
    
    def user_is_planned_act_reviewer(self, db_obj):
        '''
        this user is a planned review and review is active (DONE=1)
        '''
        users_raw = self.log_get_plan_versus_is(db_obj)
        found = 0
        for row in users_raw:
            if row['DB_USER_ID'] == session['sesssec']['user_id'] and row['DONE']==1 and row['date'] == None:
                found = 1
                break
        if found:
            answer = row
        else:
            answer = None

        return answer    

    def log_is_last_meta_review(self, db_obj, state_key):
        '''
        check for one special STATE (e.g. REVIEW)
        check if PLANNED reviews == reviews in audit log
        :param state_key:
        :return: int 0,1
        '''
        
        state_id_expect =  self.get_state_id_from_key(db_obj, state_key)
        
        log_list = self.log_get_plan_versus_is(db_obj)
        if not len(log_list):
            return 0
        
        all_found = 1
        for row in log_list:
            
            if row['STATE_ID']==state_id_expect:
                if not row['found']:
                    all_found = 0
            
        return all_found

    def signing_is_valid(self, db_obj, plan_state_id):
        '''
        check if signing is PLANNED and not yet done
        :return: {
         'valid':  int 0,1
         'reason': string 
        } 
        
        '''
        log_list = self.log_get_plan_versus_is(db_obj)
        user_id = session['sesssec']['user_id']
        is_valid = 0
        reason = '?'
        found = 0
        
        for log_row in log_list:
            
            if log_row['DB_USER_ID'] == user_id and log_row['DONE']>=1 and  log_row['STATE_ID'] == plan_state_id:
                found = 1
                datex = log_row.get('date', None)
                if datex == '' or datex is None:
                    is_valid = 1
                else:
                    reason = 'SIGNED'
                    
                break
            
        if not found:
            reason = 'NOT_FOUND'
            
        return {'valid': is_valid, 'reason': reason}
    
    @staticmethod
    def aud_log_trans_nice(db_obj, aud_log_entries):    
        '''
        transform aud log entries to nice values 
        return data by reference
        :param AUD_LOG_Struct => AUD_LOG_nice_Struct
        :return: None
        '''
        
        last_user_id = 0
        ind = 0
        for row in aud_log_entries:
    
            user_id = row['DB_USER_ID']
            if last_user_id != user_id:
                user_lib = oDB_USER.mainobj(user_id)
                user_name = user_lib.get_fullname(db_obj)
    
            aud_log_entries[ind]['USER.name']  = user_name
            state_nice    = oSTATE.STATE_info.get_nice_by_id(db_obj, row['STATE_ID'])
            aud_log_entries[ind]['STATE.name'] = state_nice
            state_key    = oSTATE.STATE_info.get_statekey_by_id(db_obj, row['STATE_ID'])
            aud_log_entries[ind]['STATE.key'] = state_key
            ind = ind + 1
            last_user_id = user_id


class Modify_obj(Obj_assoc_mod):
    """
    modify an object
    """
    states_by_key = {}
    doc_id = None
    mainlib = None
    
    def __init__(self, db_obj, objid):
        super().__init__(db_obj, 'AUD_LOG', objid)

        objlib = obj_abs('VERSION', objid)
        self.doc_id = objlib.main_feat_val(db_obj, 'DOC_ID')
        self.mainlib = Mainobj(db_obj, self.objid)
        
        # get all states
        self.states_by_key = oSTATE.STATE_info.get_all_by_key(db_obj)
        self.states_by_id = oSTATE.STATE_info.get_all_by_id(db_obj)

    def _start_wfl_action(self, db_obj, rev_type):
        '''
        start additional action for a workflow start
        '''
        audplan_lib = oAUD_PLAN.Modify_obj(db_obj, self.doc_id)
        
        start_with_status = oAUD_PLAN.REV_TYPE_REVIEW
        
        wfl_type = self.mainlib.get_doc_type_key(db_obj)
        if wfl_type == oWFL.KEY_REL_ONLY:
            # no REVIEW needed ...
            # start with RELEASE .....
            if rev_type == oAUD_PLAN.REV_TYPE_WITHDRAW:
                start_with_status = oAUD_PLAN.REV_TYPE_RELEASE
                
            if rev_type == oAUD_PLAN.REV_TYPE_RELEASE:
                start_with_status = oAUD_PLAN.REV_TYPE_RELEASE
        
        audplan_lib.review_start(db_obj, start_with_status, 1)

    def _end_wfl_action_all(self, db_obj):
        '''
        the worfkflow has finished for everybody
        '''
        audplan_lib = oAUD_PLAN.Modify_obj(db_obj, self.doc_id)
        audplan_lib.review_stop_all(db_obj)
        
    

    def _add_audit_log(self, db_obj, args):
        '''
        RAW adding of audit log, no additional actions 
        :param args
          'STATE_ID'
        '''
        
        if not args.get('STATE_ID', 0):
            raise BlinkError(1, 'Input: STATE_ID missing.')

        # TBD: check, if same audit state was there before ...

        new_pos = self.get_new_pos(db_obj, 'POS')
        args['POS'] = new_pos
        args['DB_USER_ID'] = session['sesssec']['user_id']
        args['SIGN_DATE'] = db_obj.Timestamp2Sql()
        
        self.new(db_obj, args)
        
    def get_state_id_from_KEY(self, key):
        row = self.states_by_key[key]
        state_id = row['STATE_ID']
        return state_id
    
    def _intern_review_log(self, db_obj):
        '''
        REVIEW has been finished, start release/withdraw process ...
        '''
        audplan_lib = oAUD_PLAN.Modify_obj(db_obj, self.doc_id)
        audplan_lib.review_stop(db_obj, 'REVIEW')
    
        # review start of release/withdraw process
        wf_plan = self.mainlib.get_wf_plan(db_obj)
        rw_type = oAUD_PLAN.REV_PLAN_REV_DICT[wf_plan]
        audplan_lib.review_start(db_obj, rw_type, 1)                  
               
    def _doc2pdf_decide(self, db_obj):
        '''
        decide, if the document has to be converted ....
        - do the PDF conversion 
        '''
        word_convert_flag = self.mainlib.get_def_WORD_CONVERT(db_obj)
        
        if word_convert_flag:  
            # TBD: ignore conversion errors ???
            a = Doc2Pdf(db_obj, self.objid)
            a.convert(db_obj) 
    
    def _intern_release_actions(self, db_obj):
        '''
        RELEASE has been done, post actions
       
        '''
        
        #  add a final release LOG entry + activate this version
        state_key = 'REL_END'
        arg_state_id = self.mainlib.get_state_id_from_key(db_obj, state_key)
        log_args = {
            'STATE_ID':arg_state_id
        }
        self._add_audit_log(db_obj, log_args)
        

        # do RELEASE things ...
        
        v_features = self.mainlib.features(db_obj)
        
        # TBD: deactivate old version ...
        # TBD: activate new version later on VALID_DATE !!!
        args = {
            'WFL_ACTIVE': 0,
            'RELEASE_DATE': db_obj.Timestamp2Sql(),
            'IS_ACTIVE': 1
        }
        valid_date = v_features['VALID_DATE']
        if valid_date == None:
            # if VALID_DATE is NOT set ...
            time_now  = datetime.now()
            args['VALID_DATE'] = time_now
        
        
        v_mod_obj = Obj_mod(db_obj, 'VERSION', self.objid)
        v_mod_obj.update_simple(db_obj, {'VERSION_ID': self.objid}, args)

        doc_id = self.doc_id

        args = {
            'ACT_VERS_ID':self.objid,
            'WF_PLAN' : 0
        }
        d_mod_obj = Obj_mod(db_obj, 'DOC', doc_id)
        d_mod_obj.update_simple(db_obj, {'DOC_ID': doc_id}, args)
        
        self._end_wfl_action_all(db_obj)
        
        # if document needs to be converted ...
        
        self._doc2pdf_decide(db_obj)
        
               

        # already done ...
        #audplan_lib = oAUD_PLAN.Modify_obj(db_obj, self.doc_id)
        #audplan_lib.user_did_review(db_obj, arg_state_id)  
        
    def _intern_withdraw_actions(self, db_obj):
        '''
        WITHDRAWN has been done, post actions
        '''
        
        #  add a final release LOG entry + activate this version
        state_key = 'WD_END'
        arg_state_id = self.mainlib.get_state_id_from_key(db_obj, state_key)
        log_args = {
            'STATE_ID':arg_state_id
        }
        self._add_audit_log(db_obj, log_args)
        

        # do WITHDRAW things ...
        
        # v_features = self.mainlib.features(db_obj)

        args = {
            'WFL_ACTIVE': 0,
            'IS_ACTIVE' : -1 # withdrawn
        }

        v_mod_obj = Obj_mod(db_obj, 'VERSION', self.objid)
        v_mod_obj.update_simple(db_obj, {'VERSION_ID': self.objid}, args)

        doc_id = self.doc_id

        args = {
            'ACT_VERS_ID':None,
            'WF_PLAN' : 0
        }
        d_mod_obj = Obj_mod(db_obj, 'DOC', doc_id)
        d_mod_obj.update_simple(db_obj, {'DOC_ID': doc_id}, args)
        
        self._end_wfl_action_all(db_obj)

    def sign(self, db_obj, args):

        arg_state_id = int(args['STATE_ID'])
        state_row = self.states_by_id.get(arg_state_id, {})
        state_key = ''
        if 'NAME' in state_row:
            state_key = state_row['NAME']

        while 1:
            
            if state_key == 'REL_END':
                raise BlinkError(1, 'State "' + state_key + '" not allowed here.')
                # break
            if state_key == 'WD_END':
                raise BlinkError(2, 'State "' + state_key + '" not allowed here.')
                # break            

            if state_key == 'REJECT':

                tmp_notes = args.get('NOTES', None)
                if tmp_notes == None or tmp_notes == '':
                    raise BlinkError(5, 'Please give comments on reject.')

                # here the log is added .....
                self._add_audit_log(db_obj, args)
                args = {
                    'WFL_ACTIVE': 0,
                }
                v_mod_obj = Obj_mod(db_obj, 'VERSION', self.objid)
                v_mod_obj.update_simple(db_obj, {'VERSION_ID': self.objid}, args)

                self._end_wfl_action_all(db_obj)
                break


            valid_info = self.mainlib.signing_is_valid(db_obj, arg_state_id)
            if not valid_info['valid']:
                tmp_nice=valid_info['reason']
                if valid_info['reason']=='NOT_FOUND': 
                    tmp_nice='I did not find you in the active review plan.'
                if valid_info['reason']=='SIGNED': 
                    tmp_nice='You have already signed.'                
                raise BlinkError(3, 'You are not allowed to sign. ' +tmp_nice)

            # here the log is added .....
            self._add_audit_log(db_obj, args)

            break
        #
        # finally ...
        #
        
        audplan_lib = oAUD_PLAN.Modify_obj(db_obj, self.doc_id)
        audplan_lib.user_did_review(db_obj, arg_state_id)

        # post actions ...
        
        while 1:
            
            # do review ...
            # check, if this is the last review/release for this document
            if state_key == 'REVIEW':
                is_last_review = self.mainlib.log_is_last_meta_review(db_obj, state_key)
                if is_last_review:
                    self._intern_review_log(db_obj) 
                break
            
            if state_key == 'REVIEW_REL':     
                is_last_review = self.mainlib.log_is_last_meta_review(db_obj, state_key)
                if is_last_review:
                    self._intern_release_actions(db_obj)
                break 
            
            if state_key == 'REVIEW_WD':     
                is_last_review = self.mainlib.log_is_last_meta_review(db_obj, state_key)
                if is_last_review:
                    self._intern_withdraw_actions(db_obj)
                break             
            
            break # finally ...

    def simple_log_add(self, db_obj, args):
        self._add_audit_log(db_obj, args)
    
    def _start_wfl(self, db_obj, rev_type):
        
        args = {'WFL_ACTIVE': 2}
        v_mod_obj = Obj_mod(db_obj, 'VERSION', self.objid)
        v_mod_obj.update_simple(db_obj, {'VERSION_ID': self.objid}, args)
        
        args = {'WF_PLAN': oAUD_PLAN.REV_PLAN_DICT[rev_type] }
        v_mod_obj = Obj_mod(db_obj, 'DOC', self.doc_id)
        v_mod_obj.update_simple(db_obj, {'DOC_ID': self.doc_id}, args)        
        
        self._start_wfl_action(db_obj, rev_type)        
        
    def start_r_wfl(self, db_obj):
        '''
        start Release-Workflow
        - update WFL_ACTIVE
        '''


        answer = self.mainlib.check_start_r_wfl(db_obj)
        if answer[0] < 1:
            raise BlinkError(1, 'Check Failed: ' + answer[1])
        
        args = {}
        args['STATE_ID'] = self.states_by_key['REL_START']['STATE_ID']
        self._add_audit_log(db_obj, args)
        
        rev_type = oAUD_PLAN.REV_TYPE_RELEASE
        self._start_wfl(db_obj, rev_type)
        
    def start_w_wfl(self, db_obj):
        '''
        start WITHDRAW Workflow
        - update WFL_ACTIVE
        '''


        obj_ed_lib = oVERSION_edit.Mainobj(db_obj, self.objid)
        if obj_ed_lib.workflow_is_active(db_obj):
            raise BlinkError(1, 'Workflow already active')
        
        a = Check_Wfl_Start(self.objid)
        a.check_mod_wd(db_obj)        
        
        key = oSTATE.WD_START
        args = {}
        args['STATE_ID'] = self.states_by_key[key]['STATE_ID']
        self._add_audit_log(db_obj, args)
        
        rev_type = oAUD_PLAN.REV_TYPE_WITHDRAW
        self._start_wfl(db_obj, rev_type)            
        
class Check_Wfl_Start:
    
    def __init__(self, version_id):
        self.__id = version_id
    
    def check(self, db_obj):
        '''
        check, if start Release-Workflow is possible
        :return: [
          int:     >0 ok
          string: message
        ]
        '''
        
        mainlib = Mainobj(db_obj, self.__id)
        
        obj_ed_lib = oVERSION_edit.Mainobj(db_obj, self.__id)
        if obj_ed_lib.workflow_is_active(db_obj):
            return (-1, 'Workflow already active.')
        
        users = obj_ed_lib.get_review_users(db_obj)
        if not len(users):
            return (-2, 'No review users.')
        
        v_features = mainlib.features(db_obj)
        # check VALID_DATE
        valid_date = v_features['VALID_DATE']
        if valid_date != None:
            # is smaller than now ?
            time_now  = datetime.now()
            if time_now>valid_date:
                return (-5, '"Valid-Date" is younger than time now!')

        upload_lib  = oUPLOADS.Mainobj(self.__id)
        upload_list = upload_lib.get_uploads(db_obj)
        if not len(upload_list):
            return (-3, 'No files attached.')
        
        # check doc type
        word_convert_flag = mainlib.get_def_WORD_CONVERT(db_obj)
        if word_convert_flag:
            
            # do PDF converter checks ...
            a = Doc2Pdf(db_obj, self.__id)
            try:
                a.check(db_obj)           # throws errors ...
                a.check_document(db_obj)  # check, if the document has the right KEYWORDS
                
            except Exception as exc:  
                message   = str(exc)                
                return (-4, message)
                
        return (1,'ok')
    
    def check_mod_wd(self, db_obj):
        '''
        check version for WITHDRAW workflow
        - change STATE for releasers => REVIEW_WD, because the standard workflow PLAN has REVIEW_REL
        '''
        mainlib = Mainobj(db_obj, self.__id)
        doc_id  = mainlib.doc_id
        
        obj_ed_lib = oVERSION_edit.Mainobj(db_obj, self.__id)
        users = obj_ed_lib.get_review_users(db_obj)
        if not len(users):
            raise BlinkError(1, 'No review users.')
        
        audplan_lib = oAUD_PLAN.Modify_obj(db_obj, doc_id)
        
        old_state_id = oSTATE.STATE_info.get_stateid_by_key(db_obj, oSTATE.RELEASE)
        new_state_id = oSTATE.STATE_info.get_stateid_by_key(db_obj, oSTATE.REVIEW_WD)
        
        audplan_lib.replace_plan_states(db_obj, old_state_id, new_state_id)