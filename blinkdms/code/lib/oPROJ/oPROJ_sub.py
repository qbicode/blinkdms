# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
PROJECT sub methods
File:           oPROJ_sub.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.f_utilities import BlinkError

class oPROJ_assoc_mod:
    
    def __init__(self, db_obj, proj_id):
        self.proj_id  = proj_id
        self.inserted = 0
        self.objfound = 0
        
    def add_obj(self, db_obj, tablename, objid):
        """
         * add one object to project
         * 
         *  - insert one element to project 
            - default: full insert_row() of project
            - if element exists in PROJ_HAS_ELEM, set it as link
                - on first call for project : touch project !
                - do not touch when opt["notouch"]:1
                - save proj_id as class-var
         * @param opt  
            "order"   !="" set  ELEM_ORDER
                "notouch"] : 1 : never touch project!
         * @return 0 ok
                       1 element already exists
        """
        
        if not self.proj_id :
            raise ValueError ('class not initialized')
    
        dest_table = 'PROJ_HAS_ELEM'
    
        retval = 0
        proj_id= self.proj_id
    
        db_obj.select_tuple('proj_id FROM proj_has_elem WHERE proj_id = ' + str(proj_id) +
                  ' AND DOC_ID = ' + str(objid))  # ' AND TABLE_NAME =' + db_obj.addQuotes(tablename) +

        
        if db_obj.ReadRow() and  db_obj.RowData[0] != '':
            self.objfound = self.objfound + 1
        else :
            db_obj.select_tuple('proj_id FROM proj_has_elem WHERE DOC_ID = ' + str(objid))
            # table_name = ' +  db_obj.addQuotes(tablename) +
            
            is_link = 0
            if db_obj.ReadRow() and db_obj.RowData[0] > 0:
                is_link = 1 # object already existing in a project

            argu ={}
            argu['PROJ_ID']    = proj_id
            # argu['TABLE_NAME'] = tablename
            argu['DOC_ID'] = objid
            argu['IS_LINK']    = is_link
            
            # if opt["order"]!="": argu['ELEM_ORDER'] = opt["order"]

            db_obj.insert_row(dest_table, argu)
            # on error:
            #    raise ValueError ('Insertation failed. Project (ID): ' + \
            #          str(proj_id) + '.  Object: ' + tablename + '=' + str(objid)  )

            self.inserted = self.inserted+1
        retval = 1
        
        #debug.printx( __name__, 'found?: ' + str(self.objfound) + ' inserted: '+str(self.inserted) )
    
        return retval
        
    def unlink_obj(self, db_obj, tablename, objid):
        
        if not self.proj_id :
            raise ValueError ('class not initialized')
    
        dest_table = 'PROJ_HAS_ELEM'
    
        proj_id= self.proj_id
        db_obj.del_row(dest_table, {'PROJ_ID': proj_id, 'DOC_ID': objid})  # 'TABLE_NAME':tablename,