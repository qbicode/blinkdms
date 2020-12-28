# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
folder actions
File:           oPROJ_actions.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

import sys
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin   import gPlugin

from  blinkdms.code.lib.obj.obj_info import Obj_info_lev2
#import blinkdms.code.lib.oPROJ.oPROJ_guisub as oPROJ_guisub
#import blinkdms.code.lib.oPROJ.oPROJ_sub as oPROJ_sub
from  blinkdms.code.lib.oPROJ   import oPROJ
from  blinkdms.code.lib.oPROJ.oPROJ_sub import oPROJ_assoc_mod
from blinkdms.code.lib import oROLE

from blinkdms.code.lib.f_clip import clipboard
from blinkdms.code.lib.obj import table_obj_chk



class plug_XPL(gPlugin) :  
    '''
     :var self._req_data:
       'id'
       'action'
          'cut'
          'copy'
          'paste'
          'delete'
        'sel' dictionary of selected items
    '''

    def register(self) :
        
        if 'id' not in self._req_data:
            self._req_data['id'] = -1

        self.infoarr['title']	= 'Folder actions'
        self.infoarr['layout']	= 'empty'
        self.infoarr['id']	= self._req_data['id']
        self.infoarr['role.need'] = [oROLE.ROLE_KEY_FOLDER_EDIT]

    def act_paste(self, db_obj):
        """
        use session['clip'] = {}
        """
        
        clip_lib = clipboard()  
        
        debug.printx(__name__, "session[clip]:" + str(session['clip']))
        
        if not clip_lib.len():
            return
        
        add_action=''
        do_cut= 0
        if clip_lib.get_cut_proj() is not None:
            cut_proj_id  = clip_lib.get_cut_proj()
            proj_cut_lib = oPROJ_assoc_mod(db_obj, cut_proj_id)
            add_action=' and cutted'
            do_cut = 1

        clip_lib.set_no_cut() # deactivate CUT action now

        #
        # move PROJs to new mother
        #

        for row in clip_lib:
            
            table = row['t']
            loop_proj_id = row['id']

            table_use = table
            if table != 'PROJ_ORI':
                continue  # ignore Non-PROJs

            if not do_cut:
                raise BlinkError(1, 'You cannot copy/paste a Folder.')

            proj_ori_lib = oPROJ.modify_obj(db_obj, loop_proj_id)
            proj_ori_lib.move(db_obj, self.objid)
            

        #
        # cut/paste objects (docs)
        #
        clip_lib = clipboard()  # rest iterator
        proj_mod_lib = oPROJ_assoc_mod(db_obj, self.objid)
        cnt = 0
        for row in clip_lib:
            
            table = row['t']
            tmpid = row['id']
            
            table_use = table
            if table =='PROJ_ORI':
                continue  # ignore this
            
            
            proj_mod_lib.add_obj(db_obj, table_use, tmpid) 
            if do_cut:
                proj_cut_lib.unlink_obj(db_obj, table_use, tmpid)
            cnt=cnt+1
            
        self.setMessage('OK', str(cnt) + ' Elements pasted'+add_action+'.')  
        
    def act_copy(self, sel_objects):
        """
        add objects to clipboard
        """
        
        clip_lib = clipboard()
        clip_lib.reset()
        
        cnt=0
        for l_table, elements in sel_objects.items():
            for l_objid, flag in elements.items():
                clip_lib.add( l_table, l_objid )
                cnt = cnt + 1        
            
        self.setMessage('OK', str(cnt) + ' Elements copied to clipboard.')    
        
    def act_cut(self, sel_objects):
        """
        cut objects from clipboard
        """
        
        clip_lib = clipboard()
        clip_lib.reset()
        clip_lib.set_cut(self.objid)
        
        cnt=0
        for l_table, elements in sel_objects.items():
            for l_objid, flag in elements.items():
                clip_lib.add( l_table, l_objid )
                cnt = cnt + 1        
            
        self.setMessage('OK', str(cnt) + ' Elements copied for cut to clipboard.')      
        
    def act_unlink(self, db_obj, sel_objects):
        """
        unlink
        """
        
        proj_mod_lib = oPROJ_assoc_mod(db_obj, self.objid)
    
        cnt=0
        for l_table, elements in sel_objects.items():
            for l_objid, flag in elements.items():
                
                # TBD: real projects still not supported ...
                table_use = l_table
                if l_table =='PROJ_ORI':
                    table_use = 'PROJ'                
                
                proj_mod_lib.unlink_obj(db_obj, table_use, l_objid)
                cnt = cnt + 1           
            
        self.setMessage('OK', str(cnt) + ' Elements unlinked.')  
            
    def startMain(self) :
        
        # need write access actions
        need_w_acc= [
          'paste',
          'del'
        ]
        
        sel_objects = self._req_data.get( 'sel', {} )
        
        debug.printx(__name__, "ALL:"+str(self._req_data))
        debug.printx(__name__, "sel_objects"+str(sel_objects))
        
        table = 'PROJ'
        
        db_obj = self._db_obj1
        fol_id = int(self._req_data['id'])
        self.objid = fol_id
    
        self.tablib  = table_cls(table)
        obj_lib      = obj_abs(table, fol_id)
        
        self.table_acc_mx  = table_obj_chk.get_table_rights_user(db_obj, table)
        
        if fol_id>0:
            # check if exists, do not for ROOT ...
            if not obj_lib.obj_exists(db_obj):
                raise ValueError ('Folder with ID:'+str(fol_id)+' not found.')
            
            self.obj_acc_mx    = table_obj_chk.get_object_rights_user(db_obj, table, fol_id) 
        else:
            self.obj_acc_mx = table_obj_chk.get_obj_acc_rights_DIS()
            
        if self.is_admin():
            self.obj_acc_mx['insert'] = 1 # allow ADMIN to cut, paste
            
        debug.printx(__name__, "(176) obj_acc_mx: " + str(self.obj_acc_mx))
            
        
        self.proj_lib     = oPROJ.mainobj(fol_id)  
        obj_lib_lev2      = Obj_info_lev2(table, self.objid)
        self.obj_features = obj_lib_lev2.features(db_obj)
        
        self.go_forward = 1
        
        self.action = self._req_data.get('action','')
        while(1):
           
            if self.action =='paste':
                if not self.obj_acc_mx['insert']:
                    raise BlinkError(1, 'Permission denied to insert object.')                
                self.act_paste(db_obj)
                break
            if self.action =='copy':
                self.act_copy(sel_objects)
                break  
            if self.action =='cut':
                if not self.obj_acc_mx['insert']:
                    raise BlinkError(1, 'Permission denied to cut.')
                self.act_cut(sel_objects)
                break     
            if self.action =='delete':
                if not self.obj_acc_mx['insert']:
                    raise BlinkError(1, 'Permission denied to unlink.')                
                self.act_unlink(db_obj, sel_objects)
                break
            
            # if not implemented ...
            self.setMessage('WARN', 'To be implemented!')  
            self.go_forward = 0
            
            break
        
        if self.go_forward:
            self.forward_internal_set( {'mod':'obj_one', 't':'PROJ', 'id':self.objid } ) 
        
    def mainframe(self):
        
        self.sh_main_layout()
       
        
        