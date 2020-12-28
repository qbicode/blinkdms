# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
extension for obj_list_show.py
File:           obj_list_x_ACTIVE.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.main_imports import *
from blinkdms.code.plugin.subs.obj_list_x import Obj_list_EXT

class Main(Obj_list_EXT):
    
    def get_head_cols(self):
        
        header = [

            {'show': 0,
              'nice': 'Version-ID',
              'name': 'x.VERSION_ID'
             },
            {'show': 1,
              'nice': 'Doc-ID',
              'name': 'x.C_ID'
             },
            {'show': 1,
              'nice': 'Version',
              'name': 'x.VERSION'
             },
            {'show': 1,
              'nice': 'Title',
              'name': 'x.NAME'
             },
            {'show': 1,
              'nice': 'VersionIsActive',
              'name': 'x.IS_ACTIVE'
             },
            {'show': 1,
              'nice': 'WorkflowActive',
              'name': 'x.WFL_ACTIVE'
             },  
            
            {'show': 1,
              'nice': 'Release Date',
              'name': 'x.RELEASE_DATE'
             },             
            
            {'show': 1,
              'nice': 'Notes',
              'name': 'x.NOTES'
             },
            
            {'show': 1,
              'nice': 'Owner',
              'name': 'x.DB_USER_ID'
             },
        ]
        return header
