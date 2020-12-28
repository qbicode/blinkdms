# -*- coding: utf-8 -*-
__docformat__ = "res#tructuredtext en"

"""
standard object methods: MODIFY object
File:           obj_mod.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import json 

from blinkdms.conf import config
from .main_imports import *
from .oPROJ.oPROJ_sub import oPROJ_assoc_mod
#from . import oACCESS_RIGHTS





class Singleton:

    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)

@Singleton
class Mod_helper(object):
    
    acc_grp_cache=None
    
    def grp_load_pref(self, db_obj, user_id):
        '''
        load umask_struct ( oACCESS_RIGHTS..py:GRP_ACCESS_STRUCT ) from USER_PREF
        '''
        umask_struct = {}
        sql_cmd = 'VALUE from USER_PREF where DB_USER_ID='+ str(user_id) + " and VAR_NAME='obj.new.umask'"
        db_obj.select_tuple(sql_cmd)
        if db_obj.ReadRow():
            json_str = db_obj.RowData[0]
            if len(json_str):
                umask_struct_tmp = json.loads(json_str)
                # repair structure; make key: STR => INT
                for key, val in umask_struct_tmp.items():
                    umask_struct[int(key)] = val
                
            else:
                pass
        return umask_struct
    
    def _grp_access_no_cache(self, db_obj, user_id):
        '''
        get standrad groups without usin a cache 
        - get USER_PREF
        - get personal group
        '''
        
        umask_struct = self.grp_load_pref(db_obj, user_id)
                
        # if session['globals']["security_write"]:
        # add USER personal group to matrix ...
        usrGrpId = oACCESS_RIGHTS.Methods.get_user_mygrp(db_obj, user_id)
        if usrGrpId>0: # positive value ???
            if usrGrpId not in umask_struct:
                umask_struct[usrGrpId] = oACCESS_RIGHTS.Methods.get_obj_acc_rights_ENA()     
            
        return umask_struct   
    
    def userActiveGroupsGet(self, db_obj, user_id):
        '''
        if user_id == SESSION-user:
           get obj.new.umask from local cache 
        else:
           direct query ...
           
        DB-TABLE: USER_PREF: 'obj.new.umask' : JSON( oACCESS_RIGHTS.py:GRP_ACCESS_STRUCT )
        :return: oACCESS_RIGHTS.py:GRP_ACCESS_STRUCT 
        '''
        
        session_user_id = session['sesssec']['user_id']
        if session_user_id != user_id:
            return self._grp_access_no_cache(db_obj, user_id)
        
        if self.acc_grp_cache==None:
            
            # init cache
            self.acc_grp_cache = {}
            
            self.acc_grp_cache = self._grp_access_no_cache(db_obj, user_id)
                
            if not len(self.acc_grp_cache):
                return self.acc_grp_cache                
    
            # check for inactive groups
            # check, if groups exist and is active; unset group, if not exists ...
            grp_ids = self.acc_grp_cache.keys()
            
            for groupid in grp_ids:
                sql_cmd = '1 from USER_GROUP where USER_GROUP_ID='+str(groupid)+ ' and (INACTIVE is NULL or INACTIVE<=0)'
                db_obj.select_tuple(sql_cmd)
                if db_obj.ReadRow():
                    pass
                else:
                    del( self.acc_grp_cache[groupid] )

        
        
        return self.acc_grp_cache   



# CLASSes ...

class Obj_mod:
    """
    this class should only be used by code/lib/o{TABLE}/o{TABLE}.py !!!
    higher level class: obj_mod_meta 
    
    - see also: obj_info.py: objFeatStruct
    :vartype objFeatStruct_MOD:  { 
			
        "vals" => main object parameters
          array [COL] = val
          should NOT contain CCT_ACCESS_ID
          should NOT contain a PK, if it is a single PK-object
          EXTRA_OBJ_ID will be removed
       "xobj" => array ( 
            'extra_class_id' => ... ,
            'values' 		 => array(attrib_id=>val) 
             )
        "vario" => array(
            key => val
           )
        "access" => array()
        "y" => extra form parameters, will be managed by class obj_mod_meta 
        
    
    """
    objid = None
    tablename = None
    tlib = None
    
    
    def __init__(self, db_obj, tablename, objid=None ):
        '''
        :param tablename: UPPER case string
        :param objid: ID of object, needed for all manipulation methods
        '''
        self.objid = objid
        self.tablename = tablename
        self.tlib = table_cls(tablename)
        self.infoarr=[]
    
    def set_obj(self,db_obj, objid):
        '''
        set new object
        '''
        self.objid = objid
        
    def _check_rights(self):
        # TBD: implement
        pass
        
    def _get_acc_id(self, db_obj):
        pk_name = self.tlib.pk_col_get()
        acc_id  = self.tlib.element_get_rcol(db_obj, {pk_name: self.objid}, 'CCT_ACCESS_ID')
        return acc_id
        
    def update(self, db_obj, args, options={} ):
        """
        update an OBJECT
        - check object access oACCESS_RIGHTS.
        
        :param args: objFeatStruct 
        :param options:
          'objRightsCheck' [1], -1 : do NOT check object rights
        """
        
        if not self.objid:
            raise BlinkError(1, 'Class not initialized for update.')
        
        objid     = self.objid
        tablename = self.tablename
        self._check_rights()
 
        
        table_lib = table_cls(tablename)
        pk_name   = table_lib.pk_col_get()

        
        if 'vals' in args:
            if pk_name in args['vals']:
                # remove Primary key
                del args['vals'][pk_name]
                
            db_obj.update_row(tablename, { pk_name:objid }, args['vals'])

            

    def update_simple(self, db_obj, pkarr, args):
        """
        simple update of an ELEMENT
        - NO access check!
        :param args:
          dict [COL] = val
        """
        tablename = self.tablename
        db_obj.update_row(tablename, pkarr, args)  
            
    def _anaColumns(self, main_feats):
        '''
        analyse columns, raise error on bad columns
            * @return 
            * @param object sqlo
            * @param dict main_feats
        '''                    

        PK_name  = self.tlib.pk_col_get()
        
        bad_cols = []
        
        data_type = self.tlib.get_col_DATA_TYPE(PK_name)
        if data_type != self.tlib.COL_DATA_TYPE_STRING:
            # NUMERIC IDs are not allowed, STRING-PKs are allowed ...
            bad_cols.append(PK_name)        
        
        for bad_col in bad_cols:
            if bad_col in main_feats:
                raise BlinkError(1, 'column "'+bad_col+'" not allowed.')
                

    
    def new(self, db_obj, args, options={}):
        """
        create an OBJECT
        - add to project
        - start workflow ?
        :param args: TYPEOF objFeatStruct
	:param dict options:
	  'proj_id' : if set: add to project
          'CCT_ACCESS_ID' : this id already exists, e.g. for SOCKET
          "rights"  : VARSTRUCT oACCESS_RIGHTS.py:GRP_ACCESS_STRUCT
        :return: OBJ_ID
        """
        
        self.objid = None
        tablename  = self.tablename
        
        table_lib = table_cls(tablename)
        
        pk_name  = table_lib.pk_col_get() 
        if pk_name in args['vals']:
            # remove Primary key
            data_type = table_lib.get_col_DATA_TYPE(pk_name)
            if data_type != table_lib.COL_DATA_TYPE_STRING:
                # delete if PK is NUMERIC, allow PK for strings ...
                del args['vals'][pk_name]
           
        
        # add CCT_ACCESS entry 
        #old_autocommit_val = db_obj.set_auto_commit(False)
        
        self._anaColumns(args['vals'])
  
        objid = db_obj.insert_row(tablename, args['vals'])  

        self.objid = objid # save the ID, in case an error occurs

        # db_obj.commit()
        # db_obj.set_auto_commit(old_autocommit_val) # do commit
        
        # add to project
        if options.get('proj_id',0) :
            debug.printx( __name__, 'PROJ_ADD Start' )
            proj_id = options.get('proj_id',0)
            proj_lib = oPROJ_assoc_mod(db_obj, proj_id)
            proj_lib.add_obj(db_obj, tablename, objid)
            #debug.printx( __name__, 'added to project: ' + str(proj_id) )
            self.infoarr.append('added to project ' + str(proj_id) )
            
        
        return objid
    
    def delete(self, db_obj):
        '''
        delete one object
        - do object-access check
        '''
        
        if not self.objid:
            raise BlinkError(1, 'Class not initialized for delete.')        
        
        cct_access_id = 0
        objid = self.objid
        is_bo = 0
        
        if len( self.tlib.pk_cols() ) > 1:
            #OLD: if not self.tlib.is_bo():
            raise BlinkError(1, 'Only supported for Objects with one PK.')

        tablename = self.tablename
        
        self._check_rights()
        
        obj_lib   = obj_abs(tablename, objid)
        
        if self.tlib.col_exists('CCT_ACCESS_ID'):
            is_bo = 1
            obj_feats = obj_lib.main_feat_colvals(db_obj, ['CCT_ACCESS_ID'])
            cct_access_id = obj_feats['CCT_ACCESS_ID']
        
        pk_name   = self.tlib.pk_col_get()
        pk_dict={ pk_name:objid }
        db_obj.del_row(tablename, pk_dict)
        
        if is_bo and cct_access_id:
            # remove CCT_ACCESS_ID of object
            pk_dict={ 'CCT_ACCESS_ID':cct_access_id }
            db_obj.del_row( 'CCT_ACCESS', pk_dict )    
            
    def acc_add(self, db_obj, grp_id, acc_matrix):
        '''
        add access for ONE group grp_id
        :param grp_id: int
        :param acc_matrix: acc_matrix_STRUCT
        '''
        acc_id    = self._get_acc_id(db_obj)
        right_lib = oACCESS_RIGHTS.Obj_one( acc_id )
        right_lib.acc_add(db_obj, grp_id, acc_matrix)
    
    def new_simple(self, db_obj, args_pure):
        '''
        simple insert of a NON-BO or ASSOC element
        '''
        tablename  = self.tablename
        objid = db_obj.insert_row(tablename, args_pure)
        return objid   
    
    def del_simple(self, db_obj, args_pure):
        '''
        simple DELETE of a NON-BO or ASSOC element
        '''
        db_obj.del_row(self.tablename, args_pure)
    
    def userActiveGroupsGet(self, db_obj, user_id):
        """
        get group access matrix oACCESS_RIGHTS.py:GRP_ACCESS_STRUCT 
        """
        help_lib = Mod_helper.Instance()
        return help_lib.userActiveGroupsGet(db_obj, user_id)
   
    def insert_access(self, db_obj, args, options={} ) :
        """
         * create an CCT_ACCESS entry + group oACCESS_RIGHTS.
         :param object db_obj:
         :param args: dict arguments
         :param array  options:   <pre>
         *   "rights" =  VARSTRUCT oACCESS_RIGHTS.py:GRP_ACCESS_STRUCT
         *               if a right is not set: default : 0
         *   "db_user_id" : alternative user_id for owner
             "mdo_group"  : ID of mdo_group : overwrite acc_help_tmp.mod_params()
         * @return number access_id
         """  
        
        tablename = self.tablename
    
        dest_user_id = session['sesssec']['user_id']
        if "db_user_id" in options:  dest_user_id = options["db_user_id"]

        debug.printx( __name__, 'insert_acc:' + str(args) )
    
        args['db_user_id'] = dest_user_id
        args['crea_date' ] = db_obj.Timestamp2Sql()
        args['table_name'] = tablename    
        
        
        do_mdo_group=1 # TBD ...
        if config.superglobal['app.type']=='hube' or do_mdo_group:
            from . import obj_acc_mod
            acc_help_tmp = obj_acc_mod.ins_params(tablename)
            acc_help_tmp.mod_params(db_obj, args)  
        
        if options.get("mdo_group",0)>0:
            args['OWN_GRP_ID'] = options["mdo_group"]
        
        access_id = db_obj.insert_row("CCT_ACCESS", args)
        if not access_id :
            return 0 
    
        if config.superglobal['app.type']=='hubd':
            
            # add group-rights
            if  "rights" in options : # can also contain {}, to deny group rights
                acc_many_matrix = options["rights"]
            else:
                acc_many_matrix = self.userActiveGroupsGet(db_obj, dest_user_id)
        
            if len(acc_many_matrix) :
                right_lib = oACCESS_RIGHTS.Obj_one( access_id )
                right_lib.acc_many_add(db_obj, acc_many_matrix)
            
            
    
    
        return access_id
    
   
    def touch(self, db_obj, reason={} ) :
        """
         * touch BO ( change modification time and user )
         *
         * TBD:
         *
         * @param object db_obj,  db_obj handle    
         * @param dict reason (see external-document)
         * @return array ('up':0,1, 'timest': time_obj )

         """
        pass
    
class Obj_assoc_mod:
    '''
    modify associated elements
    '''
    
    objid     = 0
    tablename = ''
    mo_table  = ''
    tlib      = None
    is_touched = 0
    
    def __init__(self, db_obj, tablename='', objid=None, opt={} ):
        '''
        :param tablename: UPPER case string of ASSOCIATED table
        :param objid: ID of object, needed for all manipulation methods
        '''
        if objid!=None: 
            self.set_obj( db_obj, tablename, objid, opt )
        
    def _check_rights(self):
        # TBD: implement
        pass        
   
    def set_obj(self, db_obj, tablename, objid, opt={} ) :
        """
         * - init an update process
         * - on first call of a MODIFICATION-function: TOUCH the mother once
         * - standard: do ACCESS-check
         * @param object db_obj
         * @param string assoctable name of assoc table, e.g. 'SPOT_RESULT'
         * @param int    objid ID of mother object
         * @param dict  opt : 
         *	'objRightsCheck' [1], -1 : do NOT check object rights
         *	FUTURE: 'oneTouch' : 0,1 - only one touch in the object-session 
         * 							(prevent many touches, when action changes)
         * @exception: error on access-violation
         """        

        self.objid     = objid
        self.tablename = tablename
        
        self.is_touched = 0
        self.tlib      = table_cls(tablename)
        self.mo_table  = self.tlib.mother_table()
        if self.mo_table=='' or self.mo_table==None:
            raise BlinkError(1, 'table "'+tablename+'" has no mother.')
        
        self.mo_t_lib      = table_cls(self.mo_table)
        
        self.pk_cols = self.tlib.pk_cols()
        self.pk = self.pk_cols[0]            

        self.mothIsBo = self.mo_t_lib.is_bo() # mother is BO ?
    
        # TBD: check access rights
        self._check_rights()
    
        
    def _touch_test(self, db_obj, act, pos, options={} ):
        '''
        - prevent multiple LOGs when many elements are added, modified ...
        act: 'new', 'mod', 'del'
        :param pos: POS of entry
        '''
        
        do_touch = 0
        if not self.is_touched:
            do_touch = 1
            
        if do_touch:

            self.is_touched = 1
    
    def _check_pk_arr(self, idarr):
        
        pk_cols = self.pk_cols
        pk      = self.pk        
        idarr[pk] = self.objid
        for pk_key in pk_cols:
            if not idarr.get(pk_key,0):
                raise BlinkError(1, 'PrimaryKey "'+pk_key+'" in Assoc-Table missing.')        
        
    def get_new_pos(self, db_obj, pos_col_name):
        '''
        get new POS for object
        :param pos_col_name: string e.g. 'POS'
        '''
        max_pos     = self.tlib.element_get_rcol(db_obj, {self.pk: self.objid} , 'max('+pos_col_name+')' )
        if max_pos is None:
            max_pos = 0
        new_pos = max_pos + 1  
        return new_pos
    
    def new(self, db_obj, args, options={}):
        args[self.pk] = self.objid
        db_obj.insert_row(self.tablename, args)
        
        
    
    def update(self, db_obj, idarr, args):

        self._check_pk_arr(idarr)
        
        db_obj.update_row( self.tablename, idarr, args )
        
        pos_col = self.pk_cols[1]
        pos_val = idarr[pos_col]
        self._touch_test(db_obj, 'mod', pos_val)
        
    def update_insert(self, db_obj, idarr, args):
        '''
        UPDATE or INSERT one element
        '''
        self._check_pk_arr(idarr)
        
        if self.tlib.element_exists(db_obj, idarr):
            self.update(db_obj, idarr, idarr)
        else:
            args = {**args, **idarr} 
            self.new(db_obj, args)
        
    def delete(self, db_obj, idarr):
        # delete one row
        
        pk_cols = self.pk_cols
        pk      = self.pk
        
        idarr[pk] = self.objid
        for pk_key in pk_cols:
            if not idarr.get(pk_key,0):
                raise BlinkError(1, 'PrimaryKey "'+pk_key+'" in Assoc-Table missing.')
        
        db_obj.del_row( self.tablename, idarr )  
        
        pos_col = self.pk_cols[1]
        pos_val = idarr[pos_col]
        self._touch_test(db_obj, 'del', pos_val)          