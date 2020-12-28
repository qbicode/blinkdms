# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
interface for ../obj_one.py


File:           DB_USER/obj_one.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.obj_sub import table_cls, obj_abs
from blinkdms.code.lib.app_plugin import html_cls

class obj_one_IF:
    
    _html_buffer =''  # optional HTML buffer of the object extension
    _req_data    = None # REQUEST data from input
    table_acc_mx = {}
    objid = None
    _obj_features = None # original object features: type: obj_info.py: objFeatStruct
    
    def set_vars(self, _html: html_cls, obj_features, table, objid, req_data):
        '''
        do NOT overwrite this !
        '''
        self._IF_vars = {}
        self._html_buffer=''
        self._html = _html
        self._obj_features = obj_features
        self.table = table
        self.objid = objid
        self._req_data = req_data
        self.table_lib = table_cls(self.table)

    def set_IF_var(self, key, val):
        self._IF_vars[key] = val
        
    def set_table_acc_mx(self, table_acc_mx):
        self.table_acc_mx = table_acc_mx
    
    def init(self, db_obj):
        # init after set_vars
        pass
       
    def get_main_config(self):
        """
        main config
        'obj.list.table'  : alternative table for object list
        'tool.allow': [1] : set to -1 to DENY access to the OBJECT-type
        'NEW.allow': 0,1
        'DEL.allow': 0,1 # allow delete ?
        'ACTIONS.but' : [
                { 'txt':'Config', 'url': 'obj_one&t=DB_USER&id=' + meta['id'] +'&action=config', 'ico': 'settings', 'itxt': 'Config' }
            ],
        'EDIT.roles': [ oROLE.BASE_ROLE.PM ]
        """
        return  {}      
        
    def x_add_html(self, text):
        """
        add HTML-text + LF
        """
        self._html_buffer = self._html_buffer + text + "\n"
        
    def mod_menu(self, menu):
        """
        menu struct:
        list of {
          'title':'object',
          'url': base_url (optional)
          'm_name':'object', 
          'submenu' : dict of new list (optional)
          'image.alias': 'settings'
          'active': 0|1 link is active?
        }
        
        example:
        [
          {'title':'object', 'm_name':'object', 'submenu': 
               [
                {'title':'preferences',  'url': base_url,   'image.alias': 'settings' },
               ]
          },
          {'title':'edit', 'm_name':'edit', 'submenu': 
              [ 
               { 'title':'Edit', 'url': base_url +'&editmode=edit', 'image.alias': 'edit-2', 'active':1  },
               { 'title':'View', 'url': base_url +'&editmode=view', 'image.alias': 'eye'  },
              ]
          }, 
                 
        ]
        """
        pass
    
    def page_bottom(self, db_obj, db_obj2, massdata):
        """
        any code on page bottom
        self._html.add_meta('bot.include',1)  
        :param massdata: dict
           'main': {}
        """
        pass
    
    def get_cols_det(self):
        '''
        column details
        answer = [
           { 'id': 'x.NAME', 'edit': 0 },
           { 'id': 'x.CONTACT_ID', 'edit': 1 },
           { 'id': 'y.last_service', 'edit': 0 },
        ]
        '''
        return []
    
    def get_columns(self):
        '''
        :return: obj_one_sub.py:col_list_seriell_STRUCT
        column details: use 'col' instead of 'id'
        answer = [
           { 'col': 'x.NAME', 'edit': 0 },
           ...
        ]
        '''
        columns_show=[]
        columns_val = self.table_lib.get_cols_allow()
        for col in columns_val:
            columns_show.append( {'col': 'x.'+col} )

        return columns_show   
    
    def get_cols_allow(self):
        answer = {}
        return answer
    
    def col_def(self, col):
        '''
        e.g. 
        if col=='CART.type':
          result = {
                'NICE_NAME':'Analyzers',
                'NOTES': 'Analyzers',
                'CCT_TABLE_NAME': None,
            }
        return result
        '''
        pass
    
    def col_select(self, db_obj, col_xcode):
        # get select list
        pass
    
    def one_data_col(self, db_obj, col, pk_val):
        pass
    
    def prep_after_check(self, db_obj):
        # activities after access check
        pass
    
    def update_pre(self, db_obj):
        # can be used to update "y" columns
        pass
    def update_after(self, db_obj):
        # can be used to update "y" columns
        pass    
        
    def plug_action(self, db_obj):
        '''
        called if go>0 and action!='' and action!='update'
        '''
        pass
        
        
    def finish_ext(self):
        '''
        TBD: still not used ... finish extension
        '''
        self._html.add_main_html(self._html_buffer)       
        
class obj_new_IF:
    '''
    extend the NEW action
    '''
    
    params = None # the form input params
    
    def forward_page(self):
        '''
        forward to other page ?
        '''
        return {}
    
    def set_vars(self, _html, table):
        '''
        FIX method, do not overwrite !
        '''
        self._html_buffer=''
        self._html  = _html
        self.table  = table
        self.params = None
        
        self.table_lib = table_cls(self.table)
        
    def set_data(self, params):
        self.params = params
    
    def get_config(self):
        return {}
        
    def init(self, db_obj):
        pass
    
    def get_columns(self):
        '''
        :return: obj_one_gui.py:main_feat_out_STRUCT
        CAN be overwritten ...
        '''
        columns_show=[]
        columns_val = self.table_lib.get_cols_allow()
        for col in columns_val:
            columns_show.append( {'col': 'x.'+col} )

        return columns_show
    
    def check_data(self, db_obj):
        '''
        CAN be overwritten ...
        check self.params
        '''        
        pass
    
    def new_after(self, db_obj, objid):
        pass    