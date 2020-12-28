# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"
"""
advanced single object info
File:           obj_info.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.obj_sub import table_cls





class Obj_info_lev2:
    """
    object info details (level2)
    
    :example:
    from blinkapp.code.lib.obj.obj_info import Obj_info_lev2
    
    obj_lib_lev2 = Obj_info_lev2( table, objid )
    obj_features = obj_lib_lev2.features(db_obj)
    
    :vartype objFeatStruct:  dict {
        "vals"  : standard values
       
        "ass"   : associated elements
                  array( $ASSOC_TABLE: array(key:val) )
        }
    
    """
    
    def __init__(self, tablename, idx):
        self.tablename = tablename
        self.__id = idx
        self._tabobj = table_cls(tablename)
        #super().__init__(tablename)
    
    def set_objid(self, id):
        self.__id = id
        
    def features(self, db_obj, options={} ):
        """
        get object features
        :param dict options:
          'rtypes' : if given, get only data from these sub-structures:
             list of "vals",  "xobj", "access" ... 
        
        :return: obj_info.py: objFeatStruct
        """
        
        result = {}
        rtypes = options.get('rtypes', [])
        pk     = self._tabobj.pk_col_get()
        
        if not len(rtypes) or ('vals' in rtypes):
            sqlsel = "* from " + self.tablename + " where  " + pk + "=" + db_obj.addQuotes(self.__id) # str( self.__id )
            db_obj.select_dict(sqlsel)
            if db_obj.ReadRow():
                result['vals'] = dict(db_obj.RowData)
            
        if self._tabobj.is_bo():
            pass
                      
        
        
            
        return result   
    
    def assoc_info(self, db_obj):
        '''
        get assoc info list
        [ {'cnt':cnt, 't'} ]
        '''
        output=[]
        
        assoc_tables = self._tabobj.get_assoc_tables(db_obj)
        for table_one in assoc_tables:
            tabl_loop_lib = table_cls(table_one)
            pk_name = tabl_loop_lib.pk_col_get()
            cnt     = tabl_loop_lib.count_elements( db_obj, {pk_name : self.__id} )
            row={'cnt':cnt, 't':table_one}
            output.append(row)
        return output
