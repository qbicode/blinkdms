# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
import CSV file
File:           f_file_csv_imp.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
import shutil
import csv
import chardet   
  
from itertools import cycle
from blinkdms.code.lib.main_imports import *



class main:
    """
    manage upload/download of files through external API
    """    
    
    column_dict = {}

    def __init__(self, filename, options={}):
        """
        :param dict options
           'delimiter' : [\t]
           DEPRECATED: 'encoding' [utf8] or ISO-8859-1
        """
        self.filename = filename
        self.delimiter='\t'
        #self.encoding = options.get('encoding', '')
        
       
        rawdata = open(self.filename, "rb").read()
        result  = chardet.detect(rawdata)
        
        charenc = result['encoding']        
        self.encoding = charenc
        
        debug.printx(__name__, "encoding: "+ str(self.encoding) )
        
    def read_header(self):
        """
        build :
        self._header
        self.column_dict
        """
        
        self._header = None
        self.column_dict = {}
        filename = self.filename
        
        with open(filename, newline='', encoding=self.encoding) as csvfile:
            reader_obj = csv.reader(csvfile, delimiter=self.delimiter)
            for row in reader_obj:
                break
        
        self._header = []
        
        pos=0
        for column in row:
            column = column.strip()
            self._header.append(column)
            self.column_dict[column] = pos
            pos = pos + 1 
        
        return self._header
    
    def get_column_dict(self):
        return self.column_dict
    
    def get_header(self):
        return self._header

    def row2dict(self, row):
        
        row_dict = {}
        pos = 0
        for value in row:
            col = self._header[pos]
            row_dict[col] = value
            pos = pos + 1
        return row_dict
    
    def open_file(self):
        
        filename = self.filename 
        
        csvfile = open(filename, newline='', encoding=self.encoding )
        self.reader_obj = csv.reader(csvfile, delimiter=self.delimiter)
        
        return  self.reader_obj  

    def close_file(self):
        self.reader_obj.close()
