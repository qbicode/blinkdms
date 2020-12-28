# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"
from flask import session
import datetime
from typing import Dict, Tuple

from blinkdms.code.lib.f_utilities import BlinkError
from blinkdms.code.lib.obj_sub import table_cls
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib import f_module_helper
from blinkdms.code.lib.obj_sql_IF import Table_sql_IF

"""
SQL command builder for a table 

         
File:           tab_abs_sql.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
class Table_sql:
    """
    - search class is extendable (for alias search) for OBJECTs by MODULE 'lib/o'+ tablename +'/tab_abs_sql'
    
    uses global vars:
    session['table.select'] : == FULL_query_STRUCT
     'sql_nice'
     'join' : 'd.DOC on d.DOC_ID=x.DOC_ID'
     'where_after': string after where conditions ...
     ]
     'colcond': [ 
       {  == one_query_cond_STRUCT
        'col' e.g. "x.EXP_ID"
        'op'  e.g. [=], 
                LIKE, 
                >=, 
                IN : e.g. 'col'=EXP_ID 'op'='IN', 'val'= '(select exp_id from XXX)'
                
        'val'     : input search value
        'val.is_name' : 0,1 : do aforeign table search, e.g. column x.DEVICE_ID, input is NAME of the device
        'nice'    : OPTIONAL nice presentation of value (e.g. x.DEV_ID, but given DEV-NAME)
        'logop'   : logical operation: BEFORE the column condition: AND, OR,
        'proj_id' : from selected PROJ_ID
        'alias'   : OPTIONAL: STRING: alias action like 'myData'
           'LOC.path.part'
        'col.type': OPTIONAL:
            'DATE' => cast column to DATE (YYYY-MM-DD), e.g. for 'col':'x.EXP_DATE' searches for exact day
       } 
     ]
       
   
    """
    
    query_dict  = {}
    session_obj = {}
    obj_ext_lib = None
    
    """
    see above session['table.select']
    """
    
    def __init__(self, tablename):
        '''
        :param tablename: UPPER case string
        '''
        self.tablename = tablename
        self.tab_lib   = table_cls(tablename)
        self.alias_lib = Aliases()
        
        # extend this class 
        path_use = 'lib/o'+self.tablename+'/tab_abs_sql'
        do_import_class=0          
        module = f_module_helper.check_module( path_use)
        if module is not None:
            if f_module_helper.module_has_class(module, 'Table_sql_x'):
                do_import_class = 1
                
        if do_import_class:          
            self.obj_ext_lib = module.Table_sql_x()        
        else:
            self.obj_ext_lib   = Table_sql_IF()        
        self.obj_ext_lib.table = self.tablename
        
        self.session_obj = session
        
        if 'table.select' not in self.session_obj:
            self.session_obj['table.select'] = {}
            
        if self.tablename not in self.session_obj['table.select']:  
            self.session_obj['table.select'][self.tablename] = {'sql_nice':''}

        self.query_dict = self.session_obj['table.select'][self.tablename].copy() # deep copy
        
        debug.printx( __name__, 'INIT_dict: ' + str(self.query_dict) )
        
    def reset(self):
        self.query_dict = {'sql_nice':''}
        
    def filter_is_active(self):
        """
        is an filter active ?
        """
        answer = 0
        if self.query_dict['sql_nice']!='':
            answer = 1
            
        return answer
    
    def count(self, db_obj):
        '''
        count elements of current selection
        '''
        sql_from = self.get_sql_from(db_obj)
        sql_cmd = "count(1) from " + sql_from
        db_obj.select_tuple(sql_cmd)
        db_obj.ReadRow()
        objcnt_sel = db_obj.RowData[0]   
        return objcnt_sel
        
    def get_sql_nice(self):
        return self.query_dict['sql_nice']
    
    def set_selection(self, id_dict):
        sel_arr = []
        self.query_dict['selobj'] = sel_arr
        self.query_dict['sql_nice'] = 'selected elements'
        
        for idx,val in id_dict.items():
            sel_arr.append(int(idx))
            
    def check_one_condition(self, one_query_cond):    
        """
        check, if the one_query_cond is valid
        :param one_query_cond: one_query_cond_STRUCT
        """
        colop   = one_query_cond.get('op','=')
        col_use = one_query_cond.get('col','')
        val_use = one_query_cond.get('val','') 
        

        output={'valid':1, 'message': ''}
        
        # normal column filter
        if val_use!='':
            if col_use =='':
                output = {'valid':0, 'message': 'Column not set'}
                
        if col_use !='' and val_use=='' and colop != 'no NULL':
            output = {'valid':0, 'message': 'Search term not set'}
            
        #TBD:  check data type ...
        return output
    
    def cond_exists(self, one_query_cond: dict):
        """
        check, if the one_query_cond already exists
        :param one_query_cond: one_query_cond_STRUCT
        """
        colop   = one_query_cond.get('op','=')
        col_use = one_query_cond.get('col','')
        val_use = one_query_cond.get('val','')   
        
        answer = 0
        loop_found=0
        
        if len( self.query_dict.get('colcond',() ) ):
            
            # test all column conditions
            
            for row in  self.query_dict['colcond']:
                
                while 1:
                    loop_found=0
                    if row.get('op','=')  != colop: break 
                    if row.get('col','=') == col_use: break
                    if row.get('val','=') == val_use: break
                    loop_found=1
                    break
                if loop_found:
                    break
        
        if loop_found:
            answer = 1
            
        return answer
    
    def add_condition(self, one_query_cond, silent=0):
        """
        add new query parameters
        :params one_query_cond:  one_query_cond_STRUCT
        :param silent: 0,1
        
        """
        if not len( self.query_dict.get('colcond',() ) ):
            self.query_dict['colcond'] = []
        
        oldlen = len(self.query_dict['colcond'])
            
        self.query_dict['colcond'].append(one_query_cond)
        if one_query_cond.get('proj_id',0) :
            if not silent: self.query_dict['sql_nice'] = 'all of '+ self.tablename + ' in Folder [ID:'+ str(one_query_cond['proj_id'])+ ']'
        else:
            logop = ' ' + one_query_cond.get('logop', 'and') + ' '
            if not oldlen:
                        logop = ''
            colop   = one_query_cond.get('op','=')
            col_use = one_query_cond.get('col','')
            val_use = one_query_cond.get('val','')  
            val_nice= one_query_cond.get('nice', val_use)  
            
            if not silent:
                        self.query_dict['sql_nice'] = self.query_dict['sql_nice'] + ' ' + logop + ' ' + col_use + ' ' + colop + ' ' + str(val_nice)

    def add_join(self, join_str):
        # 'join' : 'd.DOC on d.DOC_ID=x.DOC_ID'
        self.query_dict['join'] = join_str

    def add_condition_full(self, full_query_cond, silent=0):
        '''
        :param full_query_cond: FULL_query_STRUCT
        '''
        self.add_join(full_query_cond.get('join', ''))
        if full_query_cond.get('where_after', '') != '':
            self.query_dict['where_after'] = full_query_cond.get('where_after', '')

        many_query_cond = full_query_cond['colcond']
        
        for one_query_cond in many_query_cond:
            self.add_condition(one_query_cond, silent)
        
            
    def _get_fk(self, db_obj, col_code, val_use):
        '''
        get foreign OBJID of FOREIGN_TABLE with val_use AS PRIMARY_NAME of (self.TABLE)
        :return: int - the object ID
        '''
        
        prefix = col_code[0:2]
        col    = col_code[2:]
        
        if prefix=='x.':
            col_def = self.tab_lib.col_def(col)
              
            
            
        if col_def.get('CCT_TABLE_NAME','')=='':
            return None
        
        parent_t  = col_def['CCT_TABLE_NAME']
        table_lib = table_cls(parent_t)
        pk_name   = table_lib.pk_col_get()
        name_col  = table_lib.name_col()
        obj_id    = table_lib.element_get_rcol(db_obj, {name_col:val_use}, pk_name)
        return obj_id
        
        
    def _one_cond2sql(self, db_obj, row):
        '''
        convert one COND => SQL condition
        :param row: one_query_cond_STRUCT
        :return: string sql_one_ond
        '''
        
        pk_col = self.tab_lib.pk_col_get()
        sql_one_ond=''
        
        while 1:
            
            if row.get('proj_id',0)>0:
                # select all elements from table in project
                sql_one_ond = '( x.' + pk_col + ' in '+ \
                      ' (select PRIM_KEY from PROJ_HAS_ELEM where PROJ_ID=' + str(row['proj_id']) + \
                      ' AND TABLE_NAME='+db_obj.addQuotes(self.tablename) +')' + \
                    ' )'
                break
         
            if row.get('alias','')!='':
                
                alias = row['alias']
                
                if alias in self.alias_lib.aliases:
                    # standard alias ...
                    sql_one_ond = self.alias_lib.get_alias_cond( db_obj, alias, row )
                else:
                    # get object dependent condition
                    sql_one_ond = self.obj_ext_lib.get_alias_cond( db_obj, alias, row )
                break
            
            colop   = row.get('op','=')
            col_use = row.get('col','')    
            val_use = row.get('val','')
            
            if row.get('val.is_name',0):
                # input is NAME => but search for the object ID
                obj_id = self._get_fk(db_obj, col_use, val_use)
                debug.printx( __name__, '(260):val.is_name:  col:' + str(col_use)+' val:"'+str(val_use)+'" objid:'+str(obj_id), 1 )
                
                if obj_id is None:
                    sql_one_ond = ' (1=0)' # object not found ...
                else:   
                    sql_one_ond = ' (' + col_use + '='+ str(obj_id) + ')'
                break
            
            if val_use!='':
                val_is_numeric = 0
                try:
                    val_numeric    = float(val_use)
                    val_is_numeric = 1
                except:
                    val_is_numeric = 0
                    
                if not val_is_numeric:
                    val_use = val_use.replace('*','%')
            
            val_sql = db_obj.addQuotes(val_use) # contains quotes
            
            if colop=='LIKE':
                col_use = 'UPPER('+col_use+')'
                val_sql = 'UPPER('+val_sql+')'
                
            if colop=='IN':
                val_sql = val_use # without quotes ...     
                
            if row.get('col.type','')=='DATE':
                col_use = 'CAST('+ col_use +' AS DATE)'
            
            sql_one_ond = ' (' + col_use + ' ' + colop +' '+ val_sql + ')'
        
            break # FINAL break   
        
        return sql_one_ond 
    
    def get_sql_from(self, db_obj) -> str:
        '''
        get SQL string after "FROM"
        - handle LIKE-operator
        - VALUE: replace * by %
        INPUT: session['table.select']
        
        :return: string
        '''
        pk_col = self.tab_lib.pk_col_get()
        
        
        sql_from = ''
        sql_from = sql_from + self.tablename + ' x'
        if self.query_dict.get('join', '') != '':
            sql_from = sql_from + ' join ' + self.query_dict['join']
        
        sql_where = ''
        
        if len( self.query_dict.get('selobj',() ) ):
            
            komma=''
            selin=''
            for objid in self.query_dict['selobj']:
                selin = selin + komma + str(objid)
                komma=','
                
            sql_where = 'x.' + pk_col  + ' in ('+ selin + ')'   
        
        if len( self.query_dict.get('colcond',() ) ):
            
            # column conditions
            logop = ''
            for row in  self.query_dict['colcond']:
                
                logop = ' ' + row.get('logop', 'and') + ' '
                if logop == 'NEW':
                    logop = 'AND'
                    
                if sql_where=='':
                    logop=''
                    
                loop_sql  = self._one_cond2sql(db_obj, row)
                sql_where = sql_where + logop  + loop_sql
                
               
        
        if sql_where != '':
            sql_from = sql_from + ' where ' + sql_where
            
        if self.query_dict.get('where_after', '') != '':
            sql_from = sql_from + ' ' + self.query_dict['where_after']
        
        
        return   sql_from 
    
    def save_session(self):
        debug.printx( __name__, 'SAVE__session_dict: ' + str(self.query_dict) )
        self.session_obj['table.select'][self.tablename] = self.query_dict.copy()
    
    def get_sql_from_order_list(self, db_obj, order_list: Tuple) -> str:
        '''
        :param order_list: [ {'col':column, 'ord': 'ASC|DESC'} ]
        '''
        order_arr=[]
        for row in order_list:
            order_arr.append( row['col'] +' '+row['ord'] )
        order_str= ','.join(order_arr)
        
        return self.get_sql_from_order(db_obj, order_str)
    
    def get_sql_from_order(self, db_obj, order_str='') -> str:
        
        sql_from  = self.get_sql_from(db_obj)
        
        if order_str!='':
            #order_col = self.tab_lib.pk_col_get()
            sql_order = sql_from + " order by " + order_str
        else:
            sql_order = sql_from
            
        return sql_order
    
    def get_col_cond(self):
        '''
        get column conditions
        '''
        return self.query_dict.get('colcond', [] )
    
class Aliases:
    '''
    define default aliases ...
    '''
    
    aliases = ['DATE.1'] # allowed aliases ...
    
    def __init__(self):
        pass
    
    def _DATE_repair_date_ONE(self, date_in):
        '''
        output list of dates
        - if it is a month "2019-04" => [2019-04-01, 2019-05-01]
        0 : start date
        1 : end date
        '''
        # 
        date_out = []
        
        try:
            tmp = date_in
            if len(date_in)==4:
                tmp =  date_in + '-01-01'
            if len(date_in)==7:
                tmp =  date_in + '-01'
                
            datetime.datetime.strptime(tmp, '%Y-%m-%d')
        except:
            raise BlinkError(1, 'Bad DATE-format: "'+date_in+'"')
        
        if len(date_in)==4:
            y  = int(date_in[0:4])
            y2 = y+1
            date_out.append( date_in + '-01-01' )
            date_out.append( "%d-01-01" % y2 )
            
        elif len(date_in)==7:
            y = int(date_in[0:4])
            m = int(date_in[5:7])
            m2 = m+1
            y2 = y
            if m2>12:
                y2 = y+1
                m2 = 1
            
            date_out.append( date_in + '-01' )
            date_out.append( "%d-%02u-01" % (y2, m2) )
            
        else:
            date_out.append( date_in )
            
        return date_out

    def _DATE_between_cond(self, db_obj, date_arr, col):
        # build SQL condition for DATE
        if len(date_arr)==1:
            cond =  'CAST('+col+' AS DATE) = ' + db_obj.addQuotes(date_arr[0])
        else:
            cond =  'CAST('+col+' AS DATE) between ' + db_obj.addQuotes(date_arr[0]) + ' and ' +  db_obj.addQuotes(date_arr[1])
        return cond
    
    
    def get_alias_cond(self, db_obj, alias, one_query):
        '''
        :param one_query: one_query_cond_STRUCT (see tab_abs_sql.py)
        '''
        
        cond=''
        col = one_query['col']
         
        if alias == 'DATE.1':
            # e.g.  2019-01 2019-02
            date_many  =  one_query['val']
            row = date_many.split( '..')
            if len(row)>1:
                
                date1 = row[0].strip() # remove spaces
                val1_arr = self._DATE_repair_date_ONE(date1)
                date2 = row[1].strip() # remove spaces
                val2_arr = self._DATE_repair_date_ONE(date2)
                
                end_date = val2_arr[0]
                if len(val2_arr)>1: end_date = val2_arr[1] # it is a full month
                cond = self._DATE_between_cond( db_obj, [val1_arr[0], end_date], col )
                
            else:
                val_arr = self._DATE_repair_date_ONE(date_many)
                cond = self._DATE_between_cond(db_obj, val_arr, col)
            
        return cond    
    