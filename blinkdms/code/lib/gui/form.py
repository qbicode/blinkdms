# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
provide HTML-forms
File:           form.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.f_utilities import BlinkError

"""
 * new form class
 * @example <pre>
 * 
	import form

	initarr   = {}

	initarr["title"]       = "Select compare mode"
	initarr["submittitle"] = "Submit"

        hidden = {
            "mod": self._mod,
            "action" :  'MDO_group',
        }       

        form_obj = form( initarr, hidden, 0)

        form_fields = []
	form_fields.append ( {
		"title" : "Overview", 
		"name"  : "action",
		"object": "radio",
		"val"   : parx["action"], 
		"inits" : "overview",
		"notes" : "show only the protocol names"
                } )
	form_obj.set_form_defs( form_fields )

	formdata = form_obj.get_template_data()
        self.sh_main_layout(massdata = {'form':formdata} ) 

  </pre>

 """
class form :

    out_str = ''
    '''
    :var out_str:  the HTML buffer
    '''

    initarr = []
    hiddenarr=[]
    go = 0

    _fields    = [] 
    '''
     all fields
    :var _fields: [] of dict
     'name']  = 
     'title' = 
     'val'
     'object'
     'edit'  : int: 0,1
     'notes'
     'inits' : for select

    '''
    values_new = {}

    """
    * - init the HTML-form
    * - set <form> tag
    * - start form table
    * - manage hidden-fields
    * - variable-array: parx[]
    *
    * @param initarr <pre>
    "action"  = URL
    "ENCTYPE" = "", "multipart/form-data"
    "title"
    'submit.text'
    "editmode' = [edit], view
    'target_id': ID of MODAL div, e.g. NewProjLabel
    """
    def __init__ (self, initarr,  hiddenarr,  go  ) :

        self.initarr   = initarr
        self.hiddenarr = hiddenarr
        self.go        = go  
        self.out_str = ''

        self.go_next = self.go + 1
        self.hiddenarr['go'] = self.go_next

        if 'editmode' not in  self.initarr:
            self.initarr['editmode'] = 'edit'


    def set_form_defs(self, fields):
        self._fields = fields

    def get_template_data(self):
        """
        INPUT:  self._fields
        OUTPUT: fields for the TEMPLATE form
        """

        # ... can be empty ...
        #if not len(self._fields):
        #    raise ValueError ('Form fields are not defined.')        

        coldata = []
        for row in self._fields:

            row_out = row.copy()
            if row['object'] == 'file':
                pass
            else:
                if 'name' in row:
                    row_out['name']  = 'parx[' + row["name"] +']'

            if 'edit' in row:
                tmpval = row['edit'] 
            else: tmpval = 1
            row_out['edit'] = tmpval 

            coldata.append(row_out)

        formdata = {
            'hidden': self.hiddenarr,
            'main'  : coldata,
            'init'  : self.initarr
        }

        debug.printx( __name__, 'formdata: '+ str(formdata), 1 )

        return formdata

    def check_vals(self, values):
        """
        - check required
        - check, if column is allowed ('hidden'=1 or 'edit'=1)

        :return: sanitized values
        """

        self.values_new = {}
        col_error  = {}

        if not len(self._fields):
            raise BlinkError (1, 'Form fields are not defined.')

        # check DEFINED columns
        for row in self._fields:
            if "name" not in row:
                continue

            column   = row["name"]
            val_loop = values.get(column,'')

            val_loop = val_loop.strip()
            self.values_new[column] = val_loop

            if row.get('required',0):
                if val_loop=='':
                    col_error[column] = {'text':'value is required'}

        if len(col_error):
            raise BlinkError (2, 'Error on input: .' + str(col_error) )

        # check INPUT columns for NON-allowed data
        for key,val in self.values_new.items() :

            found=0
            # check, if KEY is allowed
            for def_row in self._fields:
                if "name" not in def_row:
                    continue

                if def_row["name"] == key:
                    found=1
                    break
            if not found:
                raise BlinkError (3, 'Column "'+key+'"not allowed.' )

            #  ('hidden'=1 or 'edit'=1)
            allow=0
            if def_row.get('hidden',0) or def_row.get('edit',1):
                allow=1
            if not allow:
                raise BlinkError (4, 'Column "'+key+'"not allowed.' )

        return self.values_new

    def get_values_new(self):
        return self.values_new
    
class f_raw:
    
    def post_dict_repair(req_data):
        """
        static
        """
        
        if type(req_data) == dict:
            # transform: 
            # parx[sql]='hallo' ===> req_data['parx']['sql']='hallo'
            # parx[sql][26]=21  ===> req_data['parx']['sql'][26]= 21
            
           
            
            keys_new = []
            for key, val in req_data.items():
                keys_new.append(key)
            
            for key in keys_new:
                pos1 = key.find('[')
                if pos1>0:
                    pos2 =key.find(']')
                    key1 =  key[0:pos1]
                    key2 =  key[pos1+1:pos2]
                    if key1 not in req_data:
                        req_data[key1] = {}
                        
                    key2_start = pos2+1
                    if key.find('[', key2_start)>=0:
                        # second index [x][y]
                        pos12 = key.find('[', key2_start)
                        pos22 = key.find(']', key2_start)
                        key3 = key[pos12+1:pos22]
                        if key2 not in req_data[key1]:
                            req_data[key1][key2] = {}
                        req_data[key1][key2][key3] = req_data[key]
                    else:
                        # single index
                        req_data[key1][key2] = req_data[key]        
    
    def argus_sanitize(argu):
        '''
        sanitize argus, remove WHITESPACEs
        :param argu: dict key:val
        '''
        
        for key, val in argu.items():
            argu[key] = val.strip()
        