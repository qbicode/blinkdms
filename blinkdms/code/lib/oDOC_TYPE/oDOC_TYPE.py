# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
TEMPLATE: get info of related objects
File:           oDOC_TYPE/oDOC_TYPE.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import json
from blinkdms.code.lib.obj_sub import table_cls, obj_abs
from blinkdms.code.lib.f_utilities import BlinkError

class Mainobj:
    """
    sinngle object class
    """
    __id = None
    obj = None  # lib obj_abs()
    
    '''
    {
        main columns: NAME; NOTES, ..
        _metadict_ : json-dictionary of METADATA
            WORD_CONVERT: 0,1 - convert to PDF ?
            DOC_CODE:   ...
            NUM_DIGITS: int
    }
    '''
    _features = None
    
    def __init__(self, id):
        self.__id = id
        self.obj = obj_abs('DOC_TYPE', id)

    def features(self, db_obj):
        '''
        warning: caches the data !
        :return: 
        '''
        if self._features != None:
            return self._features
        self._features = self.obj.main_feat_colvals(db_obj, ['*'])
        
        METADATA = self._features['METADATA']
        dictx = self._unpack_metadata(METADATA) 
        self._features['_metadict_'] = dictx

        return self._features
    
    def get_wfl_type_key(self, db_obj):
        '''
        get WFL:KEYX (workflow type KEY)
        '''
        if self._features == None:
            self.features(db_obj)
            
        wfl_id = self._features.get('WFL_ID',0) 
        if not wfl_id:
            raise BlinkError(1, 'This DOC_TYPE has no WFL_ID!')
        
        tmpobj = obj_abs('WFL', wfl_id)
        typex  = tmpobj.main_feat_val(db_obj, 'KEYX')     
        
        return typex

    def _unpack_metadata(self, METADATA):
        matadata_dict = {}
        if METADATA == None:
            return matadata_dict
        if METADATA == '':
            return matadata_dict
        
        matadata_dict = json.loads(METADATA)
        return matadata_dict
    
    def get_doc_code(self, db_obj):
        self.features(db_obj)
        dictx = self._features['_metadict_']
        codex = dictx.get('DOC_CODE', '')
        return codex
        
    def get_doc_digits(self, db_obj):
        self.features(db_obj)
        dictx = self._features['_metadict_']
        codex = dictx.get('NUM_DIGITS', '')
        return codex
    
    def get_word_convert_flag(self, db_obj):
        self.features(db_obj)
        dictx = self._features['_metadict_']
        codex = dictx.get('WORD_CONVERT', '')
        return codex      

class Table:
    """
    general table methods, static ?
    """
    def __init__(self):
        pass

    @staticmethod
    def get_all_types(db_obj):
        
        sql_cmd = "DOC_TYPE_ID, NAME from DOC_TYPE order by NAME"
        db_obj.select_tuple(sql_cmd)
   
        all_data = []
        while db_obj.ReadRow():
            xid = db_obj.RowData[0]
            name = db_obj.RowData[1]
            all_data.append({'id': xid, 'name': name})
        return all_data