# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
object history
- session['sessvars']['objhist_i'] : LAST object { 't':table, 'id':objid }
- session['sessvars']['objhist']
File:           f_objhist.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
from blinkdms.code.lib.main_imports import *

class objhist:
    '''
    manage session['sessvars']['objhist']
    - list of { 't':table, 'id':objid, 'ord': integer  }
      'ord': order first: 1
    '''
    
    def _sort_list(self):
        return sorted( session['sessvars']['objhist'], key = lambda i: i['ord']) # sort by order
    
    def clear(self):
        
        hist_struct= session['sessvars'].get('objhist',[])
        if len(hist_struct):
            hist_struct=[]
    
    def check_obj(self, table, objid):
        """
        save object in history
        """
        
        if 'sessvars' not in  session:
            return # framework not initialized ...
        
        if 'objhist' not in session['sessvars']:
            session['sessvars']['objhist'] = []
         
        if 'objhist_i' in session['sessvars']:
            if table == session['sessvars']['objhist_i']['t'] and table == session['sessvars']['objhist_i']['id']:
                return # touched before ...
            
        session['sessvars']['objhist_i'] = { 't':table, 'id':objid }
        
        hist_struct = session['sessvars']['objhist']
        

        hist_len = len(hist_struct)
        found=0
        i=0
        while i < hist_len:
            
            row = hist_struct[i]
            if row['t']==table and row['id']==objid:
                found = 1
                hist_struct[i]['ord'] = 1
            else:
                hist_struct[i]['ord'] = hist_struct[i]['ord'] + 1 # increment ORDER
            i = i + 1
            
        if not found:
            hist_struct.append( {'t':table, 'id':objid, 'ord': 1} )
            
   
    def get_objects(self):
           
        hist_struct= session['sessvars'].get('objhist',[])
            
        return hist_struct
    
    def get_CURR_oid_type(self, table):
        '''
        get most CURRENT object ID of type table
        :return: 0 or ID
        '''
           
        if not len( session['sessvars'].get('objhist',[]) ):
            return
        
        hist_cache = self._sort_list()
        
        objid_found = 0
        for row in hist_cache:
            if table == row['t']:
                objid_found = row['id']
                break
 
        return objid_found
            
    
    def get_objects_sort(self,db_obj):
        """
        get list in REVERSE order
        :return:[ {'t':, 'id':, 'nice':} ]
        """
        if 'sessvars' not in  session:
            return  []     
        
        if not len( session['sessvars'].get('objhist',[]) ):
            return []

        hist_cache = self._sort_list()
        
        output=[]
        for row in hist_cache:
            obj_lib_tmp = obj_abs(row['t'], row['id'])
            objnice     = obj_lib_tmp.obj_nice_name(db_obj)
            output.append( {'t':row['t'], 'id':row['id'], 'nice':objnice} )
            
        return output