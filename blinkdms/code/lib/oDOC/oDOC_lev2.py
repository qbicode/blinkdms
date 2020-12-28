# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
LEVEL2 DOC sub methods
File:           oDOC_lev2.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from ..obj_mod import Obj_mod
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oDOC_TYPE import oDOC_TYPE


class Modify_obj(Obj_mod):
    """
    modify an object
    """

    def __init__(self, db_obj, objid=None):
        super().__init__(db_obj, 'DOC', objid)

    def new(self, db_obj, args, options={}):
        '''
        check input
        # args
        #  'vals'
        #    'DOC_TYPE_ID'
        #    'NAME' : version name
        #  'proj_id'
        :return: Version_ID
        '''
    
        
        if 'vals' not in args:
            raise BlinkError(1, 'Input parameters missing.')

        if not args.get('proj_id', 0):
            raise BlinkError(2, 'Input: proj_id missing.')

        doc_type_id = args['vals']['DOC_TYPE_ID']

        d_vals = {'vals': {}}
        d_vals['vals']['DOC_TYPE_ID'] = doc_type_id
        d_vals['vals']['DB_USER_ID'] = session['sesssec']['user_id']
        # TBD: USERR_GROUP_ID
        
        doctype_lib = oDOC_TYPE.Mainobj(doc_type_id)
        self.META_dict = {}
        m_DOC_CODE = doctype_lib.get_doc_code(db_obj)
        m_NUM_DIGITS = doctype_lib.get_doc_digits(db_obj)

        # get last
        # TBD use other algorithm
        PREFIX = m_DOC_CODE
        sql_cmd = "count(*) from DOC where DOC_TYPE_ID=" + str(doc_type_id)
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        cnt = db_obj.RowData[0]
        next_num = cnt + 1
        format_str = "%0" + str(m_NUM_DIGITS) + "u"
        num_str = format_str % next_num
        codex = PREFIX + num_str
       
        d_vals['vals']['C_ID'] = codex

        options = {'proj_id': args['proj_id']}
        doc_id = super().new(db_obj, d_vals, options)
        
        # create new version
        v_vals = {'vals': {}}
        v_vals['vals']['NAME'] = args['vals']['NAME']
        
        versionLib = oVERSION.Modify_obj(db_obj)
        v_id = versionLib.new(db_obj, doc_id, v_vals)

        return v_id

   