# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
extension for ../obj_one.py
File:           DOC_TYPE/obj_one.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import json

from blinkdms.code.lib.obj_one_IF import obj_one_IF, obj_new_IF
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.oDOC_TYPE import oDOC_TYPE


class extend_obj(obj_one_IF):
    
    def init(self, db_obj):
        # init after set_vars
       
        doctype_lib = oDOC_TYPE.Mainobj(self.objid)
        self._more_features = doctype_lib.features(db_obj)
        
                        
    def get_columns(self):
        '''
        :return: list
        column details: use 'col' instead of 'id'
        answer = [
           { 'col': 'x.NAME', 'edit': 0 },
           ...
        ]
        '''
        columns_show=[]
        columns_val = self.table_lib.get_cols_allow()
        for col in columns_val:
            if col == 'METADATA':
                continue
            columns_show.append( {'col': 'x.'+col} )
            
        metadict = self._more_features['_metadict_']

        columns_show.append({
            'col': 'y.DOC_CODE',
            'col.nice': 'Doc code',
            'val': metadict.get('DOC_CODE',''),
            'edit': 1,
            'type': 'text',
            'required': 1
        })
        columns_show.append({
            'col': 'y.NUM_DIGITS',
            'col.nice': 'Number of digits',
            'val' : metadict.get('NUM_DIGITS',''),
            'edit': 1,
            'type': 'text',
            'required': 1
        })
        columns_show.append({
            'col': 'y.WORD_CONVERT',
            'col.nice': 'Covert Word document to PDF?',
            'val': int(metadict.get('WORD_CONVERT','0')),
            'edit': 1,
            'type': 'checkbox',
        })        

        
        debug.printx(__name__, 'EXT: self._IF_vars:' + str(self._IF_vars), 1)
        if self._IF_vars.get('editmode', '') != 'edit':
            ind = 0
            for row in columns_show:
                columns_show[ind]['edit'] = 0
                debug.printx(__name__, 'EXT: columns_show:' + str( columns_show[ind]))
                ind=ind+1


        return columns_show     
        
    def update_pre(self, db_obj):
        # can be used to update "y" columns
        # changes self._req_data['argu']
        
        argu = self._req_data['argu']

        argu['y.DOC_CODE'] = argu['y.DOC_CODE'] .strip()
        if argu['y.DOC_CODE'] == '':
            raise BlinkError(1, 'no DOC_CODE')

        argu['y.NUM_DIGITS'] = argu['y.NUM_DIGITS'] .strip()
        if argu['y.NUM_DIGITS'] == '':
            raise BlinkError(1, 'no NUM_DIGITS')
        
        argu['y.WORD_CONVERT'] = int(argu.get('y.WORD_CONVERT','0'))
               

        metavar = {
            'DOC_CODE':      argu['y.DOC_CODE'],
            'NUM_DIGITS':    argu['y.NUM_DIGITS'],
            'WORD_CONVERT':  argu['y.WORD_CONVERT']
        }

        metavar_json = json.dumps(metavar)
        self._req_data['argu']['x.METADATA'] = metavar_json
        
        #debug.printx(__name__, 'EXT: self._req_data[argu]:' + str(self._req_data['argu']))