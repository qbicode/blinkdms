# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main UPLOADs sub methods
File:           oUPLOADS.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
DB-STRUCT:
    VERSION_ID 	
    POS 	
    NAME 	
    XTYPE
"""
import os
import shutil
from datetime import datetime

from blinkdms.code.lib.main_imports import *
from ..obj_mod import Obj_assoc_mod


class Mainobj:
    
    __id = None
    obj  = None # lib obj_abs()
    
    def __init__(self, idx):
        '''
        idx = VERSION_ID
        '''
        self.__id = idx
        self._data_path = session['globals']['data_path']
        self.obj = obj_abs('UPLOADS', idx)

    def features(self, db_obj, pos):
        '''
        :return: dict
          'NAME', 
          'XTYPE'
          'file.exists'
          'file.size'
          'file.mod_date'
        '''
        if not self.__id or not pos:
            raise BlinkError(1, 'Input missing.')

        out_cols = ['NAME', 'XTYPE']
        features = db_obj.one_row_get('UPLOADS', {'VERSION_ID': self.__id, 'POS': pos}, out_cols)
        
        features['file.exists'] = self.file_exists(pos)
        features['file.size']   = self.file_size(pos)
        features['file.mod_date']  = self.mod_date_unx(pos)
        
        return features
        
    def file_path(self, pos):
        '''
        get path of the uploaded file at pos of the version
        '''
        if not self.__id or not pos:
            raise BlinkError(1, 'Input missing.')
        
        full_path = os.path.join(self._data_path, 'oDOC.' + str(self.__id) + '.' + str(pos))
        return full_path
    
    def mod_date_unx(self, pos):
        '''
        get mod_date in seconds since the epoch
        '''
        pathx = self.file_path(pos)
        if not os.path.exists(pathx):
            return 0        
        mtime = os.path.getmtime(pathx)
        
        return mtime
    
    def file_path_pdf(self, pos):
        '''
        get current path of the PDF
        '''
        if not self.__id or not pos:
            raise BlinkError(1, 'Input missing.')
        
        full_path = os.path.join(self._data_path, 'oDOC.' + str(self.__id) + '.' + str(pos) + '.pdf')
        return full_path    
    
    def file_exists(self, pos):
        pathx = self.file_path(pos)
        if not os.path.exists(pathx):
            return 0
        else:
            return 1

    def file_size(self, pos):

        pathx = self.file_path(pos)
        if not os.path.exists(pathx):
            return 0
        return os.path.getsize(pathx)

    @staticmethod
    def time_UNX2HUM(timstamp):
        output = datetime.utcfromtimestamp(timstamp).strftime('%Y-%m-%d %H:%M:%S') 
        return output
    
    def get_uploads_RAW(self, db_obj):
        '''
        get upload features RAW, without any other info ...
        '''
        sql_cmd = "* from UPLOADS where VERSION_ID=" + str(self.__id) + ' order by POS'
        db_obj.select_dict(sql_cmd)
        
        all_data = []
        while db_obj.ReadRow():
            features = db_obj.RowData 
            all_data.append(features)
            
        return all_data            

    def get_uploads(self, db_obj):
        '''
        get upload features extended ...
        '''
        sql_cmd = "* from UPLOADS where VERSION_ID=" + str(self.__id) + ' order by POS'
        db_obj.select_dict(sql_cmd)
        
        all_data = []
        while db_obj.ReadRow():
            
            features = db_obj.RowData
            
            pos = features['POS']
            
            features['file.exists'] = self.file_exists(pos)
            features['file.size']   = self.file_size(pos)
            features['file.mod_date']  = self.mod_date_unx(pos)
            features['file.mod_date_hum' ]  = Mainobj.time_UNX2HUM(features['file.mod_date'])
            
            all_data.append(features)
            
        return all_data
    
    def has_doc_file(self, db_obj):
        '''
        at least one upload is an *.docx ?
        '''
        DOC_PATTERN='.docx'
        has_doc = 0
        files = self.get_uploads(db_obj)
        if not len(files):
            return has_doc
        
        for file_loop in files:
            filename=file_loop['NAME']
            if filename.endswith(DOC_PATTERN):
                has_doc = 1
                break
        return has_doc
    
    def file_exists_in_uploads(self, db_obj, filename):
        '''
        file_exists_in_uploads ?
        '''
       
        exists = 0
        files = self.get_uploads(db_obj)
        if not len(files):
            return exists
        
        for file_loop in files:
            filename_loop=file_loop['NAME']
            if filename_loop==filename:
                exists = 1
                break
        return exists    
        

class Modify_obj(Obj_assoc_mod):
    """
    modify an object
    """
    states_by_key = {}
    pos = 0
    
    def __init__(self, db_obj, objid):
        self.pos = 0
        self._mainobj = Mainobj(objid)
        super().__init__(db_obj, 'UPLOADS', objid)

    def set_pos(self, pos):
        self.pos = pos
        
    def file_path(self):
        if not self.pos:
            raise BlinkError(1, 'Class not initialized.')
        
        return self._mainobj.file_path(self.pos)
    
    def upload_file(self, db_obj, filepath_in):
        '''
        upload file
        '''
        
        if not self.objid:
            raise BlinkError(1, 'Class not initialized.')
        if not self.pos:
            raise BlinkError(1, 'POS not initialized.')
        
        full_path_dst = self._mainobj.file_path(self.pos)
        shutil.copyfile(filepath_in, full_path_dst)
    
    def file_updated(self, db_obj):   
        '''
        FUTURE: set a log, if file was updated
        '''
        
        if not self.objid:
            raise BlinkError(1, 'Class not initialized.')
        if not self.pos:
            raise BlinkError(1, 'POS not initialized.')
        
        pass
        
        
    def set_pdf_flag(self, db_obj, pdf_flag):
        '''
        set HAS_PDF
        '''
        
        if not self.objid:
            raise BlinkError(1, 'Class not initialized.')
        if not self.pos:
            raise BlinkError(1, 'POS not initialized.')
        
        pk_arr= {'POS':self.pos}
        argu  = {'HAS_PDF':pdf_flag }
        super().update(db_obj, pk_arr, argu)


    def new(self, db_obj, args, options={}):
        
        new_pos = self.get_new_pos(db_obj, 'POS')
        args['POS'] = new_pos

        super().new(db_obj, args)
        
        return new_pos
    
    def delete_up(self, db_obj):
        '''
        delete one upload file at pos
        '''
        
        if not self.pos:
            raise BlinkError(1, 'POS not initialized.')        
        
        pkarr={'POS':self.pos}
        super().delete(db_obj, pkarr)
        
        filepath = self.file_path()
        if os.path.exists(filepath):
            os.remove(filepath) 
        

    def copy_one_upload(self, db_obj, src_data):
        '''
        copy source upload from POS in src_data to to DESTINATION
        :param src_data:
           dict of one row of UPLOADS
              'VERSION_ID', 'POS', 'NAME' , ...
        '''

        if 'VERSION_ID' not in src_data:
            raise BlinkError(1, 'Input: VERSION_ID missing.')
            
        version_src = src_data['VERSION_ID']
        pos_src = src_data['POS']
        src_obj = Mainobj(version_src)

        
        args = src_data.copy()
        del(args['VERSION_ID'])
        pos_new = self.new(db_obj, args)

        self.set_pos(pos_new)
        
        if src_obj.file_exists(pos_src):
            filepath_src = src_obj.file_path(pos_src)
            self.upload_file(db_obj, filepath_src)
