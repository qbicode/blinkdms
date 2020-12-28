# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
PROJECT GUI sub methods
File:           oPROJ_guisub.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.debug import debug

def show_path( patharr ) :
    """
    DEPRECATED :::
     show path of project
     @param list patharr
           0: ID
           1: name
    :return: string
    """        
   
    output = 'Path: ' 

    output = output + '<a href="?mod=folder&id=0"> db: </a> / '
    for proj in patharr:
        output = output + '<a href="?mod=folder&id='+ str(proj[0])+ '">' + proj[1] + '</a> / '
    
    return output
