# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
manage S_VARIO
File:           oS_VARIO.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib import oACCESS_RIGHTS
# from blinkdms.code.lib import obj_mod_helper


class Methods:
    """
    static methods
    """
    
    @staticmethod
    def getDefKeys(db_obj, tablename ) :
        """
         * get code-name of defined keys
         * @param db_obj
         """        
       
        keys = []
        db_obj.select_tuple("KEY FROM S_VARIO_DESC WHERE TABLE_NAME='" + tablename + "' order by KEY")
        while db_obj.ReadRow() :
            keys.append(db_obj.RowData[0])
    
        return keys 
    
    """
     * get all (KEY,NICE) entries
     * @param  db_obj
    """
    @staticmethod
    def getAllKeysNice(db_obj, tablename ) :
        
        keys_nice = {}
        db_obj.select_tuple("KEY, NICE FROM S_VARIO_DESC WHERE TABLE_NAME='" + tablename + "' order by NICE")
        while ( db_obj.ReadRow() ) :
            keys_nice[db_obj.RowData[0]] = db_obj.RowData[1]
        return keys_nice  
    
    
    @staticmethod
    def getDefKeyNice(db_obj, tablename, key ):
        """
         * get defined NICE-name of key
         * @param  db_obj
         * @param string key
        """        
        db_obj.select_tuple("NICE FROM S_VARIO_DESC " + 
                          " WHERE TABLE_NAME='" + tablename + "' and KEY='" + key + "'")
        db_obj.ReadRow()
        nice = db_obj.RowData[0]
        return nice    
    
    
    @staticmethod
    def all_obj_data(db_obj, tablename, objid ) :
        """
         * get all VARIO  features of (tablename, objid)
         * @param db_obj
         * @param tablename
         * @param objid
         * @return  {KEY: VALUE} 
        """  
        output={}
        
        db_obj.select_tuple("KEY, VALUE FROM S_VARIO WHERE TABLE_NAME=" + db_obj.addQuotes(tablename) + " AND OBJ_ID=" + db_obj.addQuotes(objid)  )
        while db_obj.ReadRow():
            key = db_obj.RowData[0]
            val = db_obj.RowData[1]
            output[key]=val
            
        return output

    @staticmethod
    def obj_data_by_key(db_obj, tablename, objid, key ) :
        """
        get VARIO  features of (tablename, objid, key)
        @param db_obj
        @param tablename
        @param objid
        :param key: the key
        :return: VALUE
        """  
        
        val = None
        
        db_obj.select_tuple("VALUE FROM S_VARIO WHERE TABLE_NAME=" + db_obj.addQuotes(tablename) + " AND OBJ_ID=" + db_obj.addQuotes(objid) + \
            " AND KEY=" +  db_obj.addQuotes(key) )
        if db_obj.ReadRow():
            val = db_obj.RowData[0]
          
        return val     

# ------------------------------------------

class Modify_obj :
    """
    S_VARIO modification functions
    """    
    
    isTouched = 0
   
    def __init__(self, db_obj, tablename=None, objid=None, options={} ):
        
        self.tablename = tablename
        self.objid = objid 
        self.isTouched = 0

        if objid:
            self.setObject(db_obj, tablename, objid, options )
    
    
    """
     * init object
     * @param unknown_type db_obj
     * @param unknown_type tablename
     * @param unknown_type id
     * @param array options 
       'noAccCheck':0,1
       'noTouch': 0,1
     * @return -
     """
    def setObject(self, db_obj, tablename, objid, options={} ):
        
        table_lib  = table_cls(tablename)
        self.tablename = tablename
        self.objid     = objid
        self.mothIsBo  = table_lib.is_bo()
        self.isTouched = 0
       
        if options.get('noTouch',0)>0:
            self.isTouched = 1
    
        # check access
        if options.get('noAccCheck',0)>0:
            pass
        else :
            o_rights = oACCESS_RIGHTS.Methods.access_check(db_obj, tablename, objid)
            right='insert'
            if not o_rights[right] :
                raise BlinkError( 1, 'You do not have ' + right + ' permission on object ' + tablename + ' ID:' +  str(objid) + ' !' )
    
    def del_key(self, db_obj, key):
        '''
        delete key
        '''
        idarr   = {'TABLE_NAME':self.tablename, 'OBJ_ID': self.objid, 'KEY':key }
        db_obj.del_row('S_VARIO', idarr)         

    """
     * update one value
     * - check if key exists:
     *  - yes: update
     *  - no:  insert
     * @param db_obj
     * @param key
     * @param val
     * @return unknown_type
     """
    def updateKeyVal(self, db_obj, key, val) :
        
        tablename= self.tablename
        objid    = self.objid
    
        db_obj.select_tuple("VALUE FROM S_VARIO WHERE TABLE_NAME='" + tablename + "' AND OBJ_ID=" + str(objid) + \
            " AND KEY=" +  db_obj.addQuotes(key) )
        if db_obj.ReadRow() :
            
            # do UPDATE
            argu = {}
            argu['VALUE'] = val
            idarr   = {'TABLE_NAME':tablename, 'OBJ_ID':objid, 'KEY':key }
            db_obj.update_row('S_VARIO', idarr, argu)  
    
        else :
            # INSERT
            argu={}
            argu['TABLE_NAME']=tablename
            argu['OBJ_ID']= objid
            argu['KEY']   = key
            argu['VALUE'] = val
            db_obj.insert_row('S_VARIO', argu)

        self._touchTest( db_obj, key )
    
    
    """
     * test for a touch-action
     * @param array opts : 
     *		"do" : 0,1 -- do TOUCH ?
     * @global  self._noTouch
     """
    def _touchTest(self, db_obj, key ) :
    
        if not self.mothIsBo :
            return
    
        tablename = self.tablename
        objid = self.objid
        doTouch = 0
    
        if not self.isTouched:
            doTouch = 1
    
        if doTouch:
            reason = { 'd':{'var':{'co':[key]} }, 'a':{'a':'mod'} }
            # FUTURE ...
            #obj_mod_helper.touch_row(db_obj, tablename, objid, reason )
            
    
        self.isTouched = self.isTouched + 1
    
    
