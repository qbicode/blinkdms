# -*- coding: utf-8 -*-
__docformat__ = "res#tructuredtext en"

"""
standard object methods: MODIFY object with OBJECT SPECIAL features
File:           ob_mod_meta.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib import f_module_helper
from blinkdms.code.lib.obj_mod import Obj_mod as obj_mod_abs


class obj_mod_meta:
    
    def __init__(self, db_obj, tablename, objid=None):
        '''
        :param tablename: UPPER case string
        '''
        self.tablename   = tablename
        self.obj_det_lib = None
        
        # check for OBJECT specific library
        do_import_class = 0
        module = f_module_helper.check_module('lib/o'+tablename+'/o'+tablename)
        if module is not None:
            if f_module_helper.module_has_class(module, 'modify_obj'):
                do_import_class = 1
                
        if do_import_class:
            self.obj_det_lib = module.modify_obj(db_obj, objid)
        else:
            self.obj_det_lib = obj_mod_abs(db_obj, tablename, objid)
        
    def new(self, db_obj, args, options={}):
        return self.obj_det_lib.new( db_obj, args, options)
        
    def update(self, db_obj, args):
        # :param args: objFeatStruct
        self.obj_det_lib.update(db_obj, args)
        
    def delete(self, db_obj):
        self.obj_det_lib.delete(db_obj)
            
    def set_obj(self, db_obj, objid):
        self.obj_det_lib.set_obj(db_obj,objid)
        
    def acc_add(self, db_obj, grp_id, acc_matrix):
        self.obj_det_lib.acc_add(db_obj, grp_id, acc_matrix)