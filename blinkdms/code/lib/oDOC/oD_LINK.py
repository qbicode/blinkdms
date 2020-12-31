# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main Document links  sub methods
File:           oD_LINK.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from ..obj_mod import Obj_assoc_mod

from blinkdms.code.lib.oDOC import oDOC_VERS

KEY_DEPENDS  = 1   # (M depends on C)
KEY_IS_PARENT= 2 # (M is parent of C)

KEYs_NICE= {
    1:  'depends on',
    2: 'is parent of'
}

KEYS_opposite = {
    1: 2,
    2: 1
}



class Mainobj:
    
    __id = None
    obj  = None # lib obj_abs()
    
    def __init__(self, idx):
        '''
        idx = VERSION_ID
        '''
        self.__id = idx
        self._data_path = session['globals']['data_path']
        self.obj = obj_abs('D_LINK', idx)

    def features(self, db_obj, ch_id):
        '''
        :return: dict
          'C_DOC_ID', 
          'KEY'
          
        '''
        if not self.__id or not pos:
            raise BlinkError(1, 'Input missing.')

        out_cols = ['C_DOC_ID', 'KEY']
        features = db_obj.one_row_get('D_LINK', {'M_DOC_ID': self.__id, 'C_DOC_ID': ch_id}, out_cols)

        return features

    def get_links(self, db_obj):
        '''
        get ALL OWNED links M_DOC_ID(THIS DOC) ==> C_DOC_ID
        :return [{KEY:VAL}]
        '''

        sql_cmd = "C_DOC_ID, KEY from D_LINK where M_DOC_ID=" + str(self.__id) + ' order by C_DOC_ID'
        db_obj.select_dict(sql_cmd)
        all_data = []
        while db_obj.ReadRow():
            all_data.append(db_obj.RowData)
            
        return all_data
    
    def get_other_links(self, db_obj):
        '''
        get ALL other links M_DOC_ID ==> C_DOC_ID(THIS DOC) THIS doc is not the owner
        :return [{M_DOC_ID:, KEY:}]
        '''

        sql_cmd = "M_DOC_ID, KEY from D_LINK where C_DOC_ID=" + str(self.__id) + ' order by M_DOC_ID'
        db_obj.select_dict(sql_cmd)
        all_data = []
        while db_obj.ReadRow():
            all_data.append(db_obj.RowData)
            
        return all_data    
    
    def get_links_nice(self, db_obj):
        '''
        get all LINKS direct OWNED by this document
        'C_DOC_ID'
        'KEY'
        'VERSION_ID'
        'c.name_all'
        'l.type'     : link type nice
        '''
        context = session['sesssec']['my.context']
        doc_lib1 = oDOC_VERS.Table(context)
        usetable = doc_lib1.table
        
        links = self.get_links(db_obj)

        table_lib = table_cls(usetable)

        output = []
        i = 0
        for row in links:
            
            ch_id = row['C_DOC_ID']
            key_l = row['KEY']
            key_nice = KEYs_NICE.get(key_l,'?')
            
            #??? self.obj.set_objid(ch_id)
            vers_info = table_lib.element_get(db_obj,  {'DOC_ID':ch_id}, ['C_ID', 'VERSION_ID', 'NAME'])
            if vers_info==None:
                continue # no valid VERSION for this link found
              
            new_row  = {}
            new_row['KEY']    = key_l
            new_row['DOC_ID']  = row['C_DOC_ID']
            new_row['VERSION_ID'] = vers_info['VERSION_ID']
            fullname = vers_info['C_ID'] + ' ' + vers_info['NAME']
            new_row['VERSION_ID'] = vers_info['VERSION_ID']
            new_row['c.name_all'] = fullname
            new_row['l.type'] = key_nice  
            
            output.append(new_row)
            i = i + 1
            
        return output
    
    def get_links_other_nice(self, db_obj):
        '''
        get all LINKS  OWNED by OTHER document
        'C_DOC_ID'
        'KEY'
        'VERSION_ID'
        'c.name_all'
        'l.type'     : link type nice
        ''' 
        
        context = session['sesssec']['my.context']
        doc_lib1 = oDOC_VERS.Table(context)
        usetable = doc_lib1.table
        
        links = self.get_other_links(db_obj)

        table_lib = table_cls(usetable)

        output = []
        i = 0
        for row in links:
            
            mo_id = row['M_DOC_ID']
            key_l = row['KEY']
            
            key_opposite = KEYS_opposite[key_l]
            key_nice = KEYs_NICE.get(key_opposite,'?') # do INVERSE of the key, because target DOC is the mother
            
            #??? self.obj.set_objid(ch_id)
            vers_info = table_lib.element_get(db_obj,  {'DOC_ID':mo_id}, ['C_ID', 'VERSION_ID', 'NAME'])
            if vers_info==None:
                continue # no valid VERSION for this link found
              
            new_row  = { } 
            new_row['KEY']     = key_opposite
            new_row['DOC_ID']  = row['M_DOC_ID']            
            fullname = vers_info['C_ID'] + ' ' + vers_info['NAME']
            new_row['VERSION_ID'] = vers_info['VERSION_ID']
            new_row['c.name_all'] = fullname
            new_row['l.type'] = key_nice  
            
            output.append(new_row)
            i = i + 1
            
        return output        
    
    def get_links_ALL_nice(self, db_obj):  
        # get ALL links: OWNED and OTHER links
        output1  = self.get_links_nice(db_obj)
        output2 = self.get_links_other_nice(db_obj)
        
        output = output1 + output2
        return output

class Modify_obj(Obj_assoc_mod):
    """
    modify an object
    KEY: 
       DEPENDS   (M depends on C)
       IS_PARENT (M is parent of C)
    """

    
    def __init__(self, db_obj, objid):

        self._mainobj = Mainobj(objid)
        super().__init__(db_obj, 'D_LINK', objid)

    def new(self, db_obj, args, options={}):

        if args['C_DOC_ID'] == self.objid:
            raise BlinkError(1, 'Link to itself is not allowed.')
        if args.get('KEY','') == '':
            raise BlinkError(1, 'Input:KEY missing.')        

        pks = self.pk_cols
        debug.printx(__name__, "pks:" + str(pks))
            
        table_lib = table_cls('D_LINK')
        if table_lib.element_exists(db_obj, {'M_DOC_ID': self.objid, 'C_DOC_ID': args['C_DOC_ID']}):
            # already exists
            return 
        super().new(db_obj, args)
        
        return args['C_DOC_ID']

