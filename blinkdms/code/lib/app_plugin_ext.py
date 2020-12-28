# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
the PLUGIN extend
File:           app_plugin_ext.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.oTASK import oTASK
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.obj import table_obj_chk

class gPlugin_ext:
    
    def __init__(self, _html, infoarr, mod_is_adm_space):
        self._html = _html
        self.infoarr = infoarr
        self._mod_is_adm_space = mod_is_adm_space

    def html_left(self, db_obj):
        '''
        left HTML frame update history ...
        '''
        # TBD: later ...
        #objhist_lib = objhist()
        #objects = objhist_lib.get_objects_sort(db_obj)
        #self._html.add_meta('objhist', objects)
        # if len(objects):
        #    self._html.add_meta( 'objhist_i', session['sessvars'].get('objhist_i',{})  )       
        pass
    
    def task_info(self, db_obj):
        '''
        left HTML frame update history ...
        '''

        if not session.get('loggedin', 0):
            return

        task_lib = oTASK.UserTask(session['sesssec']['user_id'])
        num = task_lib.getNumOpenTasks(db_obj)
        self._html.add_meta('task.num', num)


    def post_actions(self, db_obj):
        # self.html_left(db_obj)
        self.task_info(db_obj)

    def set_object(self, tablename, objid):
        self.tablename = tablename
        self.objid = objid

    def sec_check_obj(self, db_obj):
        '''
        do TABLE and OBJECT access checks ..
        '''
        if not self._mod_is_adm_space:  # if not in the ADMIN-Area
            return
    
        tablename = self.tablename
        # tablib   = table_cls(tablename)
    
        # if GlobMethods.is_admin():
        #    pass
        # if tablib.is_bo() :
        #    self.infoarr['table.icon.show'] = 1
        # return
 
        # throws errors
        act = {
            'tab': ['read'],
            'obj': ['read']
        }
        if len(self.infoarr.get('objtab.acc_check', {})):
            act = self.infoarr['objtab.acc_check']
                
        table_obj_chk.do_tab_obj_access_chk(db_obj, tablename, self.objid, act)


    
