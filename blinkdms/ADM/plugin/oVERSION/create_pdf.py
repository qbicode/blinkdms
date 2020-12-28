# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
create PDF from version
.. module::  create_pdf.inc
:copyright:  Blink AG   
:authors:    Steffen Kube (steffen@blink-dx.com)
"""
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin

from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oVERSION.docfile_convert import  Doc2Pdf


class plug_XPL(gPlugin) :  
    '''
     create PDF from version
    :var self._req_data:
      REQUIRED
       'id' : ID of VERSION
    '''

    def register(self) :
        
        idtmp = self._req_data.get('id',None)
        self.table='VERSION'
        try:
            self.objid = int(idtmp)
        except:
            self.objid = 0         
        
        self.infoarr['title']	= 'Create PDF from Word-file'
        self.infoarr['layout']	= 'ADM/blank'      
        self.infoarr['locrow']  = [ {'url':'ADM/home', 'text':'Home'} ]
        self.infoarr['objtype'] = self.table
        self.infoarr['id']      = self.objid        

    def startMain(self) :
        db_obj  = self._db_obj1
        
        #a = DocReplaceText(self.objid)
        #a.convert(db_obj)
        a = Doc2Pdf(db_obj, self.objid)
        a.convert(db_obj, 1)
        
        
    def mainframe(self):
        '''
       
        '''
        
     
        massdatax={}
        self.sh_main_layout( massdata=massdatax )  
