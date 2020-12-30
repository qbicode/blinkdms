# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"
"""
standard object methods
File:           obj_sub.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from flask import session
from blinkdms.code.lib.debug import debug


class table_nodb_cls:
    """
    functions without database object
    """
    
    def __init__(self, tablename):
        '''
        :param tablename: UPPER case string
        '''
        self.tablename = tablename
        
        
    def pk_col_get(self):
        '''
        get column of PK
        '''
        # TBD: replace by correct method
        # return _s_i_table[$tablename]['__table_data__']['PRIM_KEYS'][0];
        col = self.tablename + '_id'
        
        return col    


# --------------------------



class table_cls:
    """
    :example: table_lib = table_cls(table)
    """
    
    tablename=''
    COL_DATA_TYPE_STRING='NAME'
    
   
    
    """
    OLD: ...
    obj_feats={
        'EXP'  : { 'icon':'o.EXP.svg',      'nice':'experiment'},
        'ABSTRACT_PROTO': { 'icon':'o.ABSTRACT_PROTO.svg',   'nice':'assay'},
        'ABSTRACT_SUBST': { 'icon':'o.ABSTRACT_SUBST.svg',   'nice':'reagent template'},
        'CONCRETE_SUBST': { 'icon':'o.CONCRETE_SUBST.svg', 'nice':'reagent'},
        'LINK': { 'icon':'o.LINK.svg',       'nice':'document'},
        'CHIP_READER': { 'icon':'o.INSTRUMENT.svg', 'nice':'instrument'},
        'SOCKET': { 'icon':'o.SOCKET.svg',      'nice':'cartridge'},
        'PROJ': { 'icon':'o.PROJ.svg',    'nice':'folder'},
    } 
    """
    
    def __init__(self, tablename):
        '''
        :param tablename: UPPER case string
        '''
        assert (tablename !=''), "no tablename given."
        self.tablename = tablename
        
    def pk_col_get(self):
        '''
        get column of PK
        '''
        col = session['db_cache']['tables'][self.tablename]['feats']['PRIM_KEYS'][0]
        
        return col
    
    def pk_cols(self):
        '''
        get list of all PK columns
        '''
        cols = session['db_cache']['tables'][self.tablename]['feats']['PRIM_KEYS']
        
        return cols
    
    def name_col(self):
        '''
        get column of most important name
        '''
        
        col = session['db_cache']['tables'][self.tablename]['feats']['MOST_IMP_COL']   
        return col
    
    def get_col_DATA_TYPE(self, column):
        answer = session['db_cache']['tables'][self.tablename]['cols'][column]['APP_DATA_TYPE']
        return answer
    
    def tab_exists(self):
        '''
        table exists ?
        :return: 0 or 1
        '''
        answer = 0
        if self.tablename in session['db_cache']['tables']:
            answer = 1
        return answer
    
    def mother_table(self):
        '''
        get mother table
        '''
        mother = session['db_cache']['tables'][self.tablename]['feats']['CCT_TABLE_NAME']
        return mother
    
    def obj_exists(self, db_obj, objid):
        '''
        object exists ?
        :return: 0 or 1
        '''    
        #exists = 0
        #pk = self.pk_col_get()
        #value = db_obj.col_val(table, pk, objid, pk)
        #if value>0:
        #    exists = 0   
        #return exists        
        
        pkname = self.pk_col_get()
        db_obj.select_tuple(  '1 FROM '+ self.tablename +' WHERE '+ pkname + "="+ db_obj.addQuotes( str(objid) )  )
        return db_obj.ReadRow()         

   
    def element_exists(self, db_obj, where_dict, where_not={} ):
        '''
        - object exists ?
        - OPTIONAL: except condition where_not
        :param where_not: {} where NOT where_not KEY!=VAL
        :return: 0 or 1
        '''        
        exists = 0
        
        out_cols = where_dict.keys()
        
        if len(where_not):
            
            where_list = []
            for col,val in where_dict.items():
                where_list.append( col + "=" + db_obj.addQuotes(val) )
                
            where_not_list = []
            for col,val in where_not.items():
                where_not_list.append( col + "!=" + db_obj.addQuotes(val) )            
                
     
            sqlstate = ",".join(out_cols) + ' from '+ self.tablename + " where " + " and ".join(where_list) + \
                " and " + " and ".join(where_not_list)
            db_obj.select_dict( sqlstate )
            values = None
            if db_obj.ReadRow():
                # analyse one row       
                values = db_obj.RowData         
        
        else:
            values = db_obj.one_row_get( self.tablename , where_dict, out_cols )
       
        if values is not None:
            exists = 1
            
        return exists
    
    def element_get(self, db_obj, where_dict, out_cols):
        '''
        select  [out_cols] from table where {where_dict}
        '''
        return db_obj.one_row_get( self.tablename, where_dict, out_cols )
    
    def element_get_rcol(self, db_obj, where_dict, out_column):
        '''
        get out_column from table where {where_dict}
        '''
        return db_obj.col_val_where( self.tablename, where_dict, out_column )    
    
    
    def element_exist_cnt(self, db_obj, where_dict ):
        '''
        object/elements exists: return first object and number of objects
        :return dict: 
           'cnt':
           'objid':
        '''        

        objid = 0
        
        pk_col   = self.pk_col_get()
        out_cols = [pk_col,]
       
        cnt    = db_obj.count_elem(self.tablename, where_dict)
        if cnt:
           
            data_dict= db_obj.one_row_get( self.tablename , where_dict, out_cols ) 
            if data_dict is None:
                objid = 0
            else:
                objid    = data_dict.get(pk_col, 0)

        return {'cnt':cnt, 'objid': objid }     
    
    def nice_name(self):
        '''
        get nice name of table
        '''
        nice =  '???'
        if self.tablename in session['db_cache']['tables']:
            nice = session['db_cache']['tables'][self.tablename]['feats']['NICE_NAME']
        return nice
    
    def is_bo(self):
        """
        is business object ?
        """
        bo_flag = 0
        if self.tablename not in session['db_cache']['tables']:
            raise ValueError('table "' + self.tablename + '" not found in cache.')
            
        table_type = session['db_cache']['tables'][self.tablename]['feats']['TABLE_TYPE']
        if table_type == 'BO':
            bo_flag = 1

        return bo_flag

    def has_cct_access_col(self):
        """
        has a CCT_ACCESS_ID column ?
        - ignores table: "CCT_ACCESS"
        :return: 0,1
        """
        bo_flag = 0
        if self.tablename == 'CCT_ACCESS':
            return 0
        
        if 'CCT_ACCESS_ID' in session['db_cache']['tables'][self.tablename]['cols']:
            bo_flag = 1
            
        return bo_flag        
    
    def get_tab_type(self):
        table_type = session['db_cache']['tables'][self.tablename]['feats']['TABLE_TYPE']
        return table_type    
        
   
    
    def obj_icon(self):
        icon = 'o.'+self.tablename+'.svg'
        return icon
    
    def get_cols_allow(self):
        """
        :return: list of user allowed column names
        """
        col_list = []
        if self.tablename not in session['db_cache']['tables']:
            raise ValueError ("table not found in app.cache")
        
        table_cache = session['db_cache']['tables'][self.tablename]
        for col_name, col_loop in table_cache['cols'].items():
            if col_loop['VISIBLE']>0:
                col_list.append(col_name)
        
        return col_list
    
    def get_cols(self):
        """
        list of ALL column names, see also get_cols_allow()
        :return: tuple
        """
        col_list = []
        if self.tablename not in session['db_cache']['tables']:
            raise ValueError ("table not found in app.cache")
        
        table_cache = session['db_cache']['tables'][self.tablename]
        for col_name, col_loop in table_cache['cols'].items():
            col_list.append(col_name)
        
        return col_list    
    
    def col_exists(self, column_name):
        """
        return 0 or 1
        """
        answer = 0
        table_cache = session['db_cache']['tables'][self.tablename]
        if column_name in table_cache['cols']:
            answer = 1        
            return answer
        
    def col_def(self, column_name):
        """
        get MAIN definition of ONE column
        """
        table_cache = session['db_cache']['tables'][self.tablename]
        if column_name not in table_cache['cols']:
            return {}
        
        return table_cache['cols'][column_name]
    
    def col_def2(self, column_name):
        """
        get DETAILED definition of ONE column
        + 'dtype_n' : type NAME: id, name, password, float, url, ...
        + 'dtype_t' : type TYPE: 'STRING', 'INT', 'FLOAT', 'DATE'
        """
        table_cache = session['db_cache']['tables'][self.tablename]
        if column_name not in table_cache['cols']:
            return {}
        
        out = table_cache['cols'][column_name]
        app_type_id = out['APP_DATA_TYPE']
        if app_type_id:
            #type_struct = session['db_cache']['t_data']['APP_DATA_TYPE'].get(str(app_type_id), {})
            out['dtype_n'] = app_type_id.lower()  # type_struct.get('name','')
            out['dtype_t'] = 'STRING'  # TBD: !!! correct this !!! type_struct.get('type','')
        
        return out  

    
    
    def access_msg(self, right ):
        # TBD: ...
        return( 'You have no permission to '+right+' at table '  +self.tablename + \
         " Reason: You have no role right '+right+'  for this object." + \
         " Please contact the administrator to get role rights." )

    def sql_get( self, db_obj ):
        """
        get main SQL-string ('from ...')
        """  
        sql_after = 'from '+ self.tablename+ ' x where 1=1' # 1=1 is a dummy constraint to allow "AND" after that
        return sql_after        
        
   
    
   
    
    def count_elements(self, db_obj, where_dict={} ):
        '''
        count object/elements by where_dict
        :param where_dict: dict {KEY:VAL}
           if empty dict: count ALL
        :return int: count 
        '''    
        
        if not len(where_dict):
            sqlstate = 'count(1) from '+ self.tablename
            db_obj.select_tuple( sqlstate )
            db_obj.ReadRow()     
            cnt = db_obj.RowData[0]             
        else: 
            cnt  = db_obj.count_elem(self.tablename, where_dict)        
        return cnt
    
    def count_elements_where(self, db_obj, where):
        '''
        count object/elements by where_dict
        :return int: count 
        '''    
        sqlstate = 'count(1) from '+ self.tablename + " where " + where
        db_obj.select_tuple( sqlstate )
        db_obj.ReadRow()     
        cnt = db_obj.RowData[0]
        return cnt
    
    def get_assoc_tables(self, db_obj):
        '''
        get all child tables
        '''
        output=[]
        
        sql_cmd = "table_name from cct_table where CCT_TABLE_NAME=" + db_obj.addQuotes(self.tablename) + "  order by table_name"
        db_obj.select_tuple(sql_cmd)
        while db_obj.ReadRow():
            table_loop = db_obj.RowData[0]
            output.append(table_loop)      
        return output
        
    
class obj_abs:
    """
    abstract object class
    # OLD: features()
    
    :example:
    obj_lib  = obj_abs('PROJ', objid)
    """
    
    def __init__(self, tablename, idx):
        self.tablename = tablename
        self.__id = idx
        self._tabobj = table_cls(tablename)
        #super().__init__(tablename)
    
    def set_objid(self, id):
        self.__id = id
        
 
    def main_feat_colvals(self, db_obj, col_arr):
        """
        get features of selected columns in col_arr
        :param tuple col_arr: list of columns
        """
        pk = self._tabobj.pk_col_get()
        where_dict = { pk : self.__id }
        val_arr    = db_obj.one_row_get(self.tablename, where_dict, col_arr )
        return val_arr
    
    def main_feat_val(self, db_obj, col):
        """
        get features of one column
        :param string col: 
        :return :
        """
        pk = self._tabobj.pk_col_get()
        return db_obj.col_val(self.tablename, pk, self.__id, col )    
    
    def main_feat_all(self, db_obj):
        """
        get MAIN features of all columns, see also method features()
       
        """
        pk = self._tabobj.pk_col_get()
        where_dict = { pk : self.__id }
        val_arr = db_obj.one_row_get(self.tablename, where_dict, ['*'] )
        return val_arr    
    
    def obj_access(self, db_obj):
        """
        get object access matrix for user
        TBD: REMOVE this function !!!!
        USE: table_obj_chk.get_object_rights_user(db_obj, self.table, self.objid)
        """
        return { "read":1, "write":1, "delete":1, "insert":1, "entail":1}


    
    def nice_name(self):
        '''
        get nice name of table
        '''   
        return self._tabobj.nice_name()
    
    def obj_nice_name(self, db_obj, opt={} ) :
        """
         * get most important name (usually coumn NAME) of an object (SYS or BO)
         * - if object not exists: returns: "[ID:id]  NOT FOUND!"
         * @param  db_obj
         * @param  tablename
         * @param  id
         * @param  opt # "absName" : 0,1 -- with abstract name
            # "noID"    : do not return the ID, if name is empty
         """   
        
        id = self.__id
        
        tablename = self.tablename
        nice_colname   = self._tabobj.name_col()
        tmp_prim_name  = self._tabobj.pk_col_get()
        nicename   = "[ID:id]"
    
        if nice_colname != '' :
            db_obj.select_tuple( nice_colname + ' FROM ' + tablename +' WHERE '+ tmp_prim_name + ' = ' + db_obj.addQuotes(str(id)) )
            
            if db_obj.ReadRow():
                nicename = db_obj.RowData[0]
                if nicename=="" :  nicename = "[ID:id]"
                if "absName" in opt :
                    absName = self.gAbsObjName( db_obj, id, nicename )
                    if absName!="":   nicename =  nicename +  " ("+ absName +")"
    
            else:
                nicename =  nicename + " NOT FOUND!"
    
    
        return nicename   
    
   
    
    def obj_exists(self, db_obj):
        """
         * checks if an entry in the database exists (works only for single-PK objects)
         * @param object db_obj
         * @param int id ... ID of object
         """    
        
        id = self.__id
        pkname = self._tabobj.pk_col_get()
        db_obj.select_tuple(  '1 FROM '+ self.tablename +' WHERE '+ pkname+"="+ db_obj.addQuotes( str(id) )  )
        return db_obj.ReadRow()    
    
    def search_projects (self, db_obj ) :
        """ 
        search an object in the projects
        :return:  
        
        proj_arr: tuple of proj_id
        proj_id_main : main proj_id
        """
        
        proj_arr = []
        exists   = 0
        main_proj_id = 0
        
        if not self._tabobj.is_bo():
            return {'proj_arr':proj_arr, 'proj_id_main':main_proj_id }

        # TABLE_NAME='" + self.tablename + "' AND
        sqls = "PROJ_ID, IS_LINK from PROJ_HAS_ELEM where DOC_ID=" + db_obj.addQuotes(self.__id)
        db_obj.select_tuple(sqls)
        while  db_obj.ReadRow() :
            proj_id   = db_obj.RowData[0]
            is_link   = db_obj.RowData[1]
            proj_arr.append(proj_id)
            
            if not is_link: main_proj_id=proj_id    
            exists    = exists + 1
        
        if not main_proj_id and len(proj_arr):
            main_proj_id = proj_id # take last found PROJ_ID if IS_LINK is not set
    
        return {'proj_arr':proj_arr, 'proj_id_main':main_proj_id } 
    
class Obj_assoc:
    """
    abstract object class for ASSOC element
    
    :example:
    assoc_lib  = obj_assoc('DEV_LOG', objid)
    """
    
    def __init__(self, tablename, idx ):
        self.tablename = tablename
        self.__id = idx
        self._tabobj = table_cls(tablename)
        self.pks = self._tabobj.pk_cols()
        
    def get_features(self, db_obj, pos):
        """
        get values for POS of all columns as KEY:VAL
        if NO answer: None
        """
        col_arr = self._tabobj.get_cols()
        pk_dict = {
            self.pks[0] : self.__id,
            self.pks[1] : pos,
        }
        val_arr = db_obj.one_row_get(self.tablename, pk_dict, col_arr )
        return val_arr
    
    def get_one_col(self, db_obj, pos, column):
        """
        get values for POS of one column
        """
        pk_dict = {
            self.pks[0] : self.__id,
            self.pks[1] : pos,
        }
        val = db_obj.col_val_where(self.tablename, pk_dict, column )
        return val    