# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
edit reviwers/releasers

File:           doc_reved.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.oSTATE import oSTATE
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib.oVERSION import oVERSION_edit
from blinkdms.code.lib.oDOC_TYPE import oDOC_TYPE
from blinkdms.code.lib.oWFL import oWFL
from blinkdms.code.lib.gui.form import form
from blinkdms.code.lib import oROLE



class plug_XPL(gPlugin):
    '''
     :var self._req_data:
       'id' : VERSION-ID
       'reviewers' string of IDs; komma separated "1,4,5,6"
       'releasers' string of IDs; komma separated "1,4,5,6"
       'go' : 0,1  
       'parx' : ???
    '''
  
    obj_ext_lib  = None # extender class

    def register(self):

        idtmp = self._req_data.get('id', 0)
        try:
            self.objid = int(idtmp)
        except:
            self.objid = 0

        self.infoarr['title'] = 'Edit Reviewers'
        self.infoarr['layout'] = 'doc_reved'
        self.infoarr['viewtype'] = 'object'
        self.infoarr['objtype'] = 'VERSION'
        self.infoarr['id'] = self.objid
        self.infoarr['obj.id_check'] = 1
        self.infoarr['locrow.show_mo']=1
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT]
        self.infoarr['context.allow'] = ['EDIT']

    def _check_users(self, db_obj, users_str: str, state_key: str):
        '''
        check input and return allowed users
        '''
        debug.printx(__name__, '(57) state_key: '+state_key+' users (IN):' + str(users_str))
        
        reviewers=[]
        reviewer_raw = users_str.split(',')
        for raw in reviewer_raw:
            if raw !='':
                reviewers.append(int(raw))
        
        # check each user
        users_avai_raw = oDB_USER.Table.get_users_review(db_obj, state_key)
        
        cach_tmp = []
        for row in users_avai_raw:
            cach_tmp.append(row[0])
        
        not_allowed=[]
        for loop_user_id in reviewers:
            if loop_user_id not in cach_tmp:
                not_allowed.append(  oDB_USER.Table.get_fullname(db_obj, loop_user_id) )
        
        # debug.printx(__name__, '(76) reviewers: '+str(reviewers)+' cach_tmp:' + str(cach_tmp))
                
        if len(not_allowed):
            raise BlinkError(1, 'Following users are not allowed for the review/release process: ' + str(not_allowed)+'.')
 
        return reviewers

    def _update_rev_one_type(self, db_obj, reviewers: list, state_key: str):
         
        state_id = oSTATE.STATE_info.get_stateid_by_key(db_obj, state_key)
        objmod_lib = oVERSION_edit.Modify_More(db_obj, self.objid)
        objmod_lib.update_reviewers(db_obj, reviewers, state_id)
        
    def update_review_meta(self, db_obj, reviewer_str, releaser_str ):
        
        reviewers = []
        releasers = []
        #
        # check input
        #
        if self.wfl_key==oWFL.KEY_REV_REL:
            # need REVIEW + RELEASE
            if not len(reviewer_str) or not len(releaser_str):
                raise BlinkError(1, 'Need reviewers and releasers!')
            
            reviewers = self._check_users(db_obj, reviewer_str, oSTATE.REVIEW)
            releasers = self._check_users(db_obj, releaser_str, oSTATE.REVIEW)            
            
        if self.wfl_key==oWFL.KEY_REL_ONLY:
            # need RELEASE
            if not len(releaser_str):
                raise BlinkError(2, 'Need releasers!')            
        
            releasers = self._check_users(db_obj, releaser_str, oSTATE.REVIEW)        
        
        objmod_lib = oVERSION_edit.Modify_More(db_obj, self.objid)
        objmod_lib.reviewers_clean_all(db_obj)
        
        self._update_rev_one_type(db_obj, reviewers,  oSTATE.REVIEW )
        self._update_rev_one_type(db_obj, releasers,  oSTATE.RELEASE )
        
        
    def _manage_rev_users(self, db_obj, action_str):
        '''
        - analyse, which users can REVIEW, RELEASE
        
        :param action_str: 'review', 'release'
        :return: {
           'select': list of selected users
           'avai':   list of available users
        }
        '''
        
        state_id = oSTATE.STATE_info.get_stateid_by_key(db_obj, action_str)
        users_avai_raw = oDB_USER.Table.get_users_review(db_obj, action_str)

        cach_tmp = {}
        ind = 0
        for row in users_avai_raw:
            cach_tmp[row[0]] = row
            ind = ind + 1          

        users_raw = self.vers_objlib.get_review_users_by_state(db_obj, state_id)
        users_review = []
        for row in users_raw:

            user_id = row['DB_USER_ID']
            full_name = oDB_USER.Table.get_fullname(db_obj, user_id)
            users_review.append([user_id, full_name])

            if user_id in cach_tmp:
                del(cach_tmp[user_id])

        users_avai = []
        for user_id, row in cach_tmp.items():
            users_avai.append(row)
            
        return {
            'select': users_review,
            'avai':   users_avai
        }

    def startMain(self):

        db_obj = self._db_obj1
        
        self.massdata = {'form': {}}
        self._html.add_meta('id', self.objid)

        self.vers_objlib = oVERSION_edit.Mainobj(db_obj, self.objid)
       
        if not self.vers_objlib.get_current_versid(db_obj):
            raise BlinkError(1, 'This version is not valid for Edit!')
        
        if self.vers_objlib.workflow_is_active(db_obj):
            raise BlinkError(2, 'Workflow already active.')

        # available REVIEW users
        v_features = self.vers_objlib.features(db_obj)
        
        d_type_id = v_features['vals'].get('DOC_TYPE_ID', 0)
        if not d_type_id:
            raise BlinkError(3, 'This document has no doc_type!')
        
        doc_type_lib = oDOC_TYPE.Mainobj(d_type_id)
        self.wfl_key = doc_type_lib.get_wfl_type_key(db_obj)
        
        if self.wfl_key==oWFL.KEY_REV_REL:
            
            tmp_rev_info = self._manage_rev_users(db_obj, oSTATE.REVIEW)
            self.massdata['show.review']   = 1 
            self.massdata['users.review']   = tmp_rev_info['select'] 
            self.massdata['users.rev.avai'] = tmp_rev_info['avai'] 
        
        if self.wfl_key!= oWFL.KEY_NO_WORKFLOW:

            tmp_rev_info = self._manage_rev_users(db_obj, oSTATE.RELEASE)
            self.massdata['show.release']   = 1 
            self.massdata['users.release']  = tmp_rev_info['select'] 
            self.massdata['users.rel.avai'] = tmp_rev_info['avai']        

        # parx = self._req_data.get('parx', {})

        if int(self._req_data.get('go', '0')) > 0:

            reviewer_str  = self._req_data.get('reviewers', '')
            releasers_str = self._req_data.get('releasers', '')
            self.update_review_meta(db_obj, reviewer_str, releasers_str)
           

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
    
 
        
        