# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""

.. module::  login.py
:copyright:  Blink AG   
:authors:    Steffen Kube <steffen@blink-dx.com>
"""
from flask import session

from blinkdms.code.lib.app_plugin import gPlugin
# from blinkdms.ots.gozilla_jsonrpc import gozilla_jsonrpc
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.login import login
from blinkdms.code.lib.db import db

# from blinkdms.code.lib.oROLE    import oROLE
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib import oROLE

import sys, time

class plug_XPL(gPlugin) :  
   

    def register(self) :

        self.infoarr['title']	= 'Login'
        self.infoarr['layout']	= 'login'
        self.infoarr['session.need'] = -1


    def startMain(self) :
        '''
        :param go: 0,1
        :param user: string
        :param password: string
        :param cid:  [OPTIONAL] DOC code e.g. 'SOP-0001'
        :param old_mod: [OPTIONAL] forward to module xxx
        '''
        
        user_in=''
        password_in=''
        
        go = 0
        if 'go' in self._req_data:
            go   = self._req_data['go']

        
        if 'user' in self._req_data:
            user_in     = self._req_data['user'].strip()
        if 'password' in self._req_data:
            password_in = self._req_data['password'].strip()
        
        # self._session = {}   # delete session data

        if not go:

            if self._req_data.get('old_mod', '') != '':
                # save it in meta to cache the forward module ...
                self._html.add_meta('old_mod', self._req_data['old_mod'])
                self._html.add_meta('cid', self._req_data.get('cid', ''))
            return

        # delete session data, after login try
        session['loggedin'] = 0    # deactivate
        session['sesssec']  = {}

        if (user_in==None or password_in==None) :
            self.setMessage('ERROR', 'User or password missing.')
            return

        # dbid = 'blk' #
        dbid    = self._superglobal['db.std_config_id']  # standard DB for HUBE
        access_config = self._superglobal['db'][dbid]
        
        access_config_tmp = access_config.copy()
        access_config_tmp['password']='***'
        debug.printx(__name__, "(72) dbid:"+  str(dbid) +' config:'+str(access_config_tmp) )
        
        db_obj1 = db()
        db_obj1.open( access_config )        

        login_obj = login(session)
        
        username_use = user_in

        try :
            
            login_result = login_obj.check_login(db_obj1, user_in, password_in)
            username_use = login_result['nick']
            user_id      = login_result['user_id']
            debug.printx(__name__, "LOGIN_RES:"+  str(login_result)  )
          
            
        except ValueError as err:
            
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.setMessage('ERROR', str(exc_value) ) 
            return

        
        login_obj.initvars(db_obj1, username_use, password_in, dbid, user_id, access_config)
        
        # check allowed context
        user_lib = oDB_USER.mainobj(user_id)
        roles = user_lib.get_roles(db_obj1)
        if oROLE.ROLE_KEY_EDIT not in roles:
            # has no EDIT role ...
            session['sesssec']['my.context'] = 'ACTIVE' 


        req_data = {
            'mod': 'home'
        }

        # forward to a document ?
        if self._req_data.get('old_mod', '') == 'doc_edit':
            if self._req_data.get('cid', '') != '':
                req_data = {
                    'mod': 'doc_edit',
                    'cid': self._req_data.get('cid', '')
                }

        self.forward_internal_set(req_data)
        
        if self.is_rest:
            self.rest_data = {'active':1 }
           
