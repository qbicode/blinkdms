# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
clipboard functions
File:           f_clip.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *

class clipboard:
    """
    provides an iterator
    """
    
    def __init__(self):
        self.index = 0    
    
    def __iter__(self):
        return self    
    
    def __next__(self):
        if self.index >= len(session['clip']):
            raise StopIteration
        last_ind   = self.index
        self.index = self.index + 1
        return session['clip'][last_ind]    
    
    def reset(self):
        session['clip'] = []
        session['sessvars']['clipboard'] = None
        self.index = 0
    
    def set_no_cut(self):
        session['sessvars']['clipboard'] = None
        
    def set_cut(self, proj_id):
        session['sessvars']['clipboard'] = {'cut_proj_id':proj_id }
        
    def add(self,table, objid):
        session['clip'].append( {'t':table, 'id':objid} )
        
    def len(self):
        return len(session['clip'])    
    
    def get_cut_proj(self):
        """
        get CUT proj_id
        """
        
        if session['sessvars'].get('clipboard', None) is None:
            return None
        
        proj_id = session['sessvars']['clipboard']['cut_proj_id']
        
        return proj_id