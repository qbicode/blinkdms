'''
OBJECT LIST: import data
'''
import os
import traceback
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.gui.form import form
from blinkdms.code.lib import f_workdir
from blinkdms.code.lib import f_file_csv_imp
from blinkdms.code.lib.gui.table import Table

from werkzeug.utils import secure_filename

import sys

class plug_XPL(gPlugin) :  
    '''
     * 
     * @package ol.import.py
     * @author  Steffen Kube (steffen@blink-dx.com)
     @param  parx
     't' : table
     'action':
         'insert'
         'update'
         'insupd'
     @param go  0,1,2
     
    '''
    
    formobj = None

    def register(self) :

        self.infoarr['title']	= 'Object: import data for root'
       
        self.infoarr['layout'] = 'ADM/ol_import'
        self.infoarr['admin.only'] = True
        self.infoarr['locrow']  = [ 
            {'url':'ADM/home', 'text':'Home'},
        ]        

    
    def _init1( self, go, parx, filename_full) :

        self.go = go
        self.filename_full = filename_full
        self.parx = parx
        
        
        table_lib   = table_cls(self.table)
        if not table_lib.tab_exists():
            raise BlinkError(1,'Table "'+table+'" not exists')

        
    
    def help(self) :
    
    
           
        self.html_add ( "Short help" )
    
        self.html_add ( '''
                <ul>
                    <li>Tipp: Statements for Oracle must <em>not</em> end with a semicolon () !!! </li>
                <li>Restriction: if the user is NOT "root": only the command 'SELECT' is allowed!</li>
                    <li>CSV-format: LINEFEED '\n' will be replaced by pattern <b>LF_pattern</b></li>
                    <li>SQL-Example: select * from exp where exp_id < 1000</li>
    
                </ul>
                ''') 
          
    
        self.html_add ( "<br>" )
    

    
    def _ana_header(self, header, header_pos_dict):
        
        self._info = {}
        table_lib   = table_cls(self.table)
        self._info['PKs']      = table_lib.pk_cols()
        self._info['pos_dict'] = header_pos_dict
        
        is_bo = table_lib.is_bo()
        
        if is_bo:
            raise BlinkError(1,'UnderConstruction: data fromBO-objects is not supported.')
        
        for column in header:
            # TEMPORARY no check
            # if not table_lib.col_exists(column):
            #    raise BlinkError(1,'Column "'+column+'" not found in DB')
            
            #col_feats = table_lib.col_def(column)
            pass
            
    def do_one_row(self, db_obj, row_dict_raw):
        """
        return OBJ_ID (can be a string)
        """
        tablename = self.table
        
        # check, if object exists
        pks = self._info['PKs']

        row_dict = {}
        for key, val in row_dict_raw.items():
            if key != '':
                row_dict[key]=val
        
        where_dict = {  }
        
        if len(pks)==1 and tablename!='CCT_TABLE':
            # single PK do not ask for PK
            for pk_col in pks:
                if pk_col in row_dict:
                    val = row_dict[pk_col]
                    where_dict[pk_col] = val            
        else:
            # MULTI PKs

            for pk_col in pks:
                val = row_dict[pk_col]
                where_dict[pk_col] = val
        
        action = self.action
        
        # TBD: support insupd
        if len(where_dict):
            if self.table_lib.element_exists( db_obj, where_dict ):
                
                action='update'
                # remove primary keys from data
                for pk_col in pks:
                    del row_dict[pk_col]           
            
        
        debug.printx(__name__, "ACT: go:" + str(self.go) + ' action:' + action + ' where:' + str(where_dict) + ' row_dict:' + str(row_dict))
        
        if self.go == 2:
            
            if action == 'insert':   
                objid = db_obj.insert_row( tablename, row_dict )  
            else:
                
                # update 
                pk1   = pks[0]
                objid = where_dict[pk1]
                db_obj.update_row(tablename, where_dict, row_dict)
        else:
            objid = '???'
            
        return {'objid': objid, 'mess': 'action:'+  action }
    
    """
     * the main export loop
     * @return 
     * @param object db_obj
     * @global string outmode
     * @global array parx
     """
    def do_import(self, db_obj ) :
        
        self.table_lib   = table_cls(self.table)
        
        csvlib = f_file_csv_imp.main(self.filename_full)
        header = csvlib.read_header()
        header_pos_dict = csvlib.get_column_dict()
        
        self._ana_header(header, header_pos_dict)
        
        file_obj = csvlib.open_file()
        
        cnt=0
        self.messages = []
        rows_cache=[]
        
        for row in file_obj:
            
            debug.printx(__name__, "ROW:"+ str(cnt) )
            rows_cache.append(row)
            
            if not cnt: 
                cnt=cnt+1
                continue # header
            
            row_dict = csvlib.row2dict(row)
            try:
                row_answer = self.do_one_row(db_obj, row_dict)
                message = {'status': 'ok', 'mess': str(row_answer) }
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()  
                err_stack = traceback.extract_tb(exc_traceback)
                row_answer = '?'
                #  debug.printx(__name__, "exc_traceback:"+ repr(err_stack) )      
                message =  {'status': 'error', 'mess': str(exc_value) + ' STACK: '+ repr(err_stack) }
                
            #  self.html_add ( "INFO:"+ message +': ' + str(row_answer) + ': '+str(row_dict) + '<br>\n' )   
            self.messages.append(message)    
            cnt=cnt+1
 
    
        self.file_data = Table.list2table(rows_cache)
    
    def form1(self):
        
        #tables_allow= ['CCT_COLUMN', 'CCT_TABLE', 'STOCK_H_E']
        #tables_select= { }
        #for tab_loop in tables_allow:
        #    tables_select[tab_loop] = tab_loop
        
        parx = {}
        if 'parx' in self._req_data:
            parx = self._req_data['parx']

        initarr   = {}
        
        initarr["title"]       = "Import data file"
        initarr["startform"]   = 1 
        initarr["submittitle"] = "Prepare"
        initarr["ENCTYPE"]     = "multipart/form-data"
    
        hiddenarr = {}
        hiddenarr["mod"]     = self._mod        
        self.formobj = form(initarr, hiddenarr, 0)
       
        fields = []
        fieldx = {
            "title" : "Action", 
            "name"  : "action",
            "object": "select",
            "inits": [ ['insert', 'insert'], ['update', 'update'] , ['inupd', 'insupd'] ],
            "val"   : '', 
            "notes" : "Table"
            }
        fields.append( fieldx )         
        
        fieldx = {
            "title" : "Table", 
            "name"  : "t",
            "object": "text",
            "val"   : '', 
            "notes" : "Table"
            }
        fields.append( fieldx )                
        
        fieldx = {
            "title" : "Data file", 
            "name"  : "dataf",
            "object": "file",
            "val"   : '', 
            "notes" : "The data file"
            }
        fields.append( fieldx )        

        self.formobj.set_form_defs( fields ) 
    
    def form2(self):


        initarr   = {}  
        initarr["title"]       = "Do import now"
        initarr["startform"]   = 1 
        initarr["submittitle"] = "Import"
      
    
        hiddenarr = {}
        hiddenarr["mod"]          = self._mod    
        hiddenarr["parx[t]"]      = self.table   
        hiddenarr["parx[action]"] = self.action   
        
        self.formobj = form(initarr, hiddenarr, 1)
        self.formobj.set_form_defs( [] ) 
    
    def startMain(self):
        
        db_obj = self._db_obj1
        self.formobj = None
        
        debug.printx(__name__, "REQUEST:"+ str(self._req_data) )
        
        go    = int( self._req_data.get('go', 0))
        parx  = self._req_data.get( 'parx', {} )
        table = parx.get('t', '')
        self.table = table
        
        action = parx.get('action', '')
        self.action = action
        self.messages = []

        self.file_data = None
        dest_fileShort = 'datafile.csv'
        
        if not go :
            debug.printx(__name__, "show form:" )
            # self.form1() 
            self.html_add ( self.form1() ) 
            
            self.help()
            return
        
        if go==1:
            
            debug.printx(__name__, "file:"+ str( self._req_data['__FILES__']) )
            
            if table=='':
                raise ValueError ('No table given.')
            if action=='':
                raise ValueError ('No Action given.')            
            
            self.html_add ( self.form2() )        
            
            work_lib = f_workdir.main()
            work_dir = work_lib.getWorkDir( 'ol_import' )            
            
            if '__FILES__' not in self._req_data:
                raise ValueError ('No file found.')
            
            if 'dataf' not in self._req_data['__FILES__']:
                raise ValueError ('No data file found.')                
            
            file = self._req_data['__FILES__']['dataf']

            filename      = secure_filename(file.filename)
            filename_full =  os.path.join( work_dir, dest_fileShort)
            file.save(filename_full )  
        

        if go==2:
            
            work_lib = f_workdir.main()
            work_dir = work_lib.getWorkDir( 'ol_import', 1 )            
             
            filename_full =  os.path.join( work_dir, dest_fileShort)

        self._init1(go, parx, filename_full)   
            
        self.do_import(db_obj)

            
    def mainframe(self):
        
        db_obj = self._db_obj1

        massdata = {}
        massdata ['messages'] =   self.messages
        massdata ['file_data'] =  self.file_data

        if self.formobj:

            formdata = self.formobj.get_template_data()
            massdata['form'] = formdata
        self.sh_main_layout(massdata = massdata )        
        
        
             
