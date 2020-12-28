# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
main PROJECT sub methods
File:           oPROJ.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.obj_mod import Obj_mod
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib import oROLE
from blinkdms.code.lib.obj import table_obj_chk


class mainobj:
    
    __id = None
    obj  = None # lib obj_abs()
    
    def __init__(self, id):
        """
        :param id: can be 0 (for root)
        """
        self.__id = id
        self.obj = obj_abs('PROJ', id)
    
    def _get_sql_base_where(self):
        """
        get base after where 
        """
        proj_id  = self.__id
        sql_cond = '=' + str(proj_id)
        if not proj_id:
            sql_cond = ' is NULL' # the root ...
        
        sql_cond = 'PRO_PROJ_ID' + sql_cond
        
        return sql_cond
    
    def get_path_arr(self, db_obj, stopProjID=0, stopLevel=0) :
        """*
         * get project path as array  (ID, NAME)
         * @param unknown db_obj
         * @param unknown projid
         * @param number stopProjID  ID of project to stop getting the parent-project
         * @param number stopLevel : number of levels where to stop scanning ( 2 : stop )
                                                      - if stopped: save flag in self.stopLevelReached
                                                      
         * @return array : index = 0 : first proj-id after ROOT
            ( (proj_id, proj_name) )
         """        
    
        MAX_LEVEL	= 10
        depth_cnt	= 0
        current_projid = self.__id
        path_arr       = []
        stopLevelGot   = 0
        if not stopLevel : 
            stopLevel = MAX_LEVEL
        self.stopLevelReached = 0
    
        while ( current_projid and (depth_cnt < MAX_LEVEL) ) :
    
            if stopProjID and (stopProjID == current_projid) :
                break
    
            sql_sel= "pro_proj_id, name, proj_id from proj  where proj_id=" + str(current_projid)
            db_obj.select_tuple(sql_sel)
            if db_obj.ReadRow() :
                if depth_cnt >= (stopLevel-1) :
                    stopLevelGot = 1
                    break
                current_projid = db_obj.RowData[0]
                master_name    = db_obj.RowData[1]
                last_proj_id   = db_obj.RowData[2]
                subarr = (last_proj_id, master_name)
                path_arr.append(subarr)

            else :
                break
    
            depth_cnt = depth_cnt + 1
    
    
        if stopLevelGot: 
            self.stopLevelReached = depth_cnt

        path_arr.reverse()   # noe reverse to have the array in the real customer order     
    
        return path_arr    
    
    def get_path_str(self, db_obj, stopProjID=0, stopLevel=0) :
        '''
        get Path as string
        '''
        path_arr = self.get_path_arr(db_obj, stopProjID, stopLevel)
        path_str=''
        for row in path_arr:
            path_str = path_str +'/' + row[1]
        
        return path_str
    
    def elem_of_table_SQL (self, table ) :
        '''
        get all objects of one type
        '''
        proj_id  = self.__id
        sqlAfter = "select DOC_ID from PROJ_HAS_ELEM where PROJ_ID=" + str(proj_id)  # FUTURE: " AND TABLE_NAME='"+table+"'"
        return sqlAfter
    
    def getTableSQLInSort(self, table, pkname='', nameCol=''):
        '''
        get SQL-command to select all PROJ_HAS_ELEM of type=TABLE; usage select * FROM {sqlafter}
        :return: STRING sqlafter
        '''
        
        
        objlib = table_cls(table)
        if pkname == '':
            pkname = objlib.pk_col_get()
        
        if pkname=='' :
            raise ValueError ('table ' + table + ' is not defined or has no PK.')

        if nameCol == '':
            nameCol = objlib.name_col()
            
        if nameCol=='':
            raise ValueError ('table ' + table + ' has no importantName.')
    
        sqlafter = self.elem_of_table_SQL ( table )
        sqlafter = table + " x where x." + pkname + " IN (" + sqlafter + ") order by x." + nameCol
        
        return sqlafter
    
   
    def tables_in_proj(self, db_obj):
        # get all distinct tables in project
        
        proj_id  = self.__id
        
        tables = []
        sqlsel = "distinct(DOC_ID) from PROJ_HAS_ELEM where PROJ_ID=" + str(proj_id)  # + " order by TABLE_NAME"
        db_obj.select_tuple(sqlsel)
        if db_obj.ReadRow():
            tables = ['DOC']

        return tables    
        
    def cnt_elems_of_table(self, db_obj, table):
        proj_id  = self.__id
        sqlsel = "count(1) from PROJ_HAS_ELEM where PROJ_ID=" + str(proj_id)  # FUTURE: +" AND TABLE_NAME='"+table+"'"
        db_obj.select_tuple(sqlsel)
        db_obj.ReadRow()
        cnt   = db_obj.RowData[0]    
        return cnt
    
    def _oneTypeAnalyse(self, db_obj, tablename, maxobj) :
        """
         * type analysis of ONE table type
         * @param unknown db_obj
         * @param unknown tablename
         * @return {
            'cnt':
            'elem' : [ {'id':, 'name':} ] -- max maxobj elements
         }
         """            

        if tablename=='PROJ_ORI' :
            # get sub-projects
            objarr = self.sub_projects_nice(db_obj)
            return {'cnt':len(objarr), 'elem':objarr }

        #objlib = table_cls(tablename)
        pkname = 'DOC_ID'  # objlib.pk_col_get()
        # if pkname == '':
        #    raise ValueError ('table "'+tablename+'" has no defined PK.')

        cntelem = self.cnt_elems_of_table(db_obj, tablename)
        nameCol = 'C_ID'  # objlib.name_col()
        
        
        sqlAfter = self.getTableSQLInSort(tablename, pkname, nameCol)
        sqlsel  = "x." + pkname + ", x." + nameCol + " from " + sqlAfter
        db_obj.select_tuple(sqlsel)
        objarr=[]
        cnt = 0
        while db_obj.ReadRow()  :
            if cnt >= maxobj:
                # break, if too many objects
                break
            tmpid   = db_obj.RowData[0]
            tmpname = db_obj.RowData[1]

            objarr.append( {'id':tmpid, 'name':tmpname} )
            cnt = cnt + 1

        return {'cnt':cntelem, 'elem':objarr }

    def sub_projects_id(self,db_obj) :
        """
         * get all sub-projects of project, order by NAME
         * @param  db_obj
         * @param  int proj_id : if "0" : convert the id to NULL
         * @return array of IDs
         """ 
        
    
        # Important: the order by replace() is needed, because POSTGRES ignores the DOT char on ordering !
        sqlsel="PROJ_ID FROM proj WHERE " + self._get_sql_base_where() + " ORDER BY replace(name, '.', '0')"
        db_obj.select_tuple(sqlsel)
        projarr=[]
        while db_obj.ReadRow():
            projarr.append(db_obj.RowData[0])
    
        return projarr 
        
    def sub_projects_nice(self, db_obj):
        '''
        :return: list of {'id':, 'name':}
        '''
        projIds = self.sub_projects_id(db_obj)
        
              

        oneObjArr=[]
        
        if len(projIds)>0 : # tables exist
            
            for subProjID in projIds:
                objlib  = obj_abs('PROJ', subProjID)
                tmpname = objlib.obj_nice_name ( db_obj )
                oneObjArr.append( {'id':subProjID, 'name':tmpname} )
    
        return oneObjArr
    
    def proj_name_exists(self, db_obj, name_in):
        """
        if project exists: return ID of project
        """
        sqlsel="PROJ_ID FROM proj WHERE "+ self._get_sql_base_where() +" and (name like "+db_obj.addQuotes(name_in) +")"
        db_obj.select_tuple(sqlsel)
        found_id = 0
        if db_obj.ReadRow():
            found_id = db_obj.RowData[0]        
        
        return found_id
    
    def obj_name_exists(self, db_obj, table, name_in):
        """
        if obejct exists in PROJ: return ID of project
        """
        
        table_lib = table_cls(table)
        pk_col   = table_lib.pk_col_get()
        name_col = table_lib.name_col()
        
        proj_id  = self.__id
        sqlAfter0 = "select DOC_ID from PROJ_HAS_ELEM where PROJ_ID=" + str(proj_id)  # +" AND TABLE_NAME='"+table+"'"
        sqlsel    = pk_col + ' from '+table+' where '+name_col+'='+db_obj.addQuotes(name_in) +  \
            ' and '+pk_col+' in ('+sqlAfter0+')'
              
        db_obj.select_tuple(sqlsel)
        found_id = 0
        if db_obj.ReadRow():
            found_id = db_obj.RowData[0]        
        
        return found_id


    def get_proj_arr_names(self, db_obj, proj_list):
        '''
        get names
        '''
        objlib_tmp = obj_abs('PROJ', 0)

        proj_names=[]
        cnt=0
        for proj_id in proj_list:

            if cnt>10:
                proj_names.append({'id':0, 'nice':'... more ...'})
                break

            if proj_id == self.__id:
                continue

            objlib_tmp.set_objid(proj_id)
            nice = objlib_tmp.obj_nice_name(db_obj)
            proj_names.append({'id':proj_id, 'nice':nice})
            cnt=cnt+1

        return proj_names    
    
    def get_objects(self, db_obj, tables=[], maxobj=2000):
        '''
        get all objects of one PROJ
        - for table=DOC : get DOC_IDs
        :param db_obj: database object
        :param list tables: list of names
        :param maxobj:
        :return: dict of
            TABLE_NAME : {
              'cnt': int, -- real count 
              'elem' : [ {'id':, 'name':} ] -- max maxobj elements
            }
          }
        '''
        
       
        objarr = {}
        objarr['PROJ_ORI'] = {'elem': self.sub_projects_nice(db_obj) }
        objarr['PROJ_ORI']['cnt'] = len(objarr['PROJ_ORI']['elem']) 
        
        if not self.__id:
            # for rrot project
            return objarr
        
        if len(tables) :
            # only one specific tabel-type
            for table_loop in tables :
                if table_loop=='PROJ_ORI' :
                    continue # already collected ...
        
                oneObjArr = self._oneTypeAnalyse(db_obj, table_loop, maxobj)
                objarr[table_loop] = oneObjArr
        
        
        
        else :
            # get all tables, all objects
    
            tables = self.tables_in_proj( db_obj ) 
            if len(tables): # tables exist
                
                for oneTable in tables :
                    oneObjArr = self._oneTypeAnalyse(db_obj, oneTable, maxobj)
                    objarr[oneTable] = oneObjArr
        
        return objarr
    
    # get parent project
    def getParentProj(self, db_obj) :
        proj_id  = self.__id
        
        sqlsel = "PRO_PROJ_ID from PROJ where PROJ_ID =" + str(proj_id)
        db_obj.select_tuple(sqlsel)
        id_out = 0
        if db_obj.ReadRow():
            id_out = db_obj.RowData[0]
            if id_out is None:
                id_out = 0
        return id_out
    
class modify_obj(Obj_mod):
    """
    modify/create a project
    checks ROLE + GROUP rights on actions ...
    """
    
    def __init__(self, db_obj, objid=None ):
        super().__init__(db_obj, 'PROJ', objid)
        
   
       

    def check_rights(self, db_obj, right_key):
        '''
        checks summary of OBJECT rights + ROLE rights
        :throws: errors
        :param right_key: e.g. 'write' or 'delete'
        '''
        
        if not self.objid:
            raise BlinkError(1, 'Input: Object-ID not set.')
        
        obj_acc_matrix  = table_obj_chk.get_object_rights_user(db_obj, 'PROJ', self.objid)
        user_lib = oDB_USER.mainobj(session['sesssec']['user_id'])
        can_edit_folders = user_lib.has_role(db_obj, oROLE.ROLE_KEY_FOLDER_EDIT)
        if not can_edit_folders:
            raise BlinkError(1, 'You need role '+oROLE.ROLE_KEY_FOLDER_EDIT+' to "'+right_key+'" this folder.')
        
        if not obj_acc_matrix[right_key]:
            raise BlinkError(2, 'You have no group-right "'+right_key+'" on this folder.')
            
        return 1
        
       
    def new(self, db_obj, args, options={} ):
        '''
        do access check of mother !
        check for 'insert'
        :param options: insert options
          "rights"  : VARSTRUCT oACCESS_RIGHTS.py:GRP_ACCESS_STRUCT
          'objRightsCheck' [1], -1 : do NOT check object rights
        '''

        args['vals']['DB_USER_ID'] = session['sesssec']['user_id']
        args['vals']['CREA_DATE'] = db_obj.Timestamp2Sql()

        mother_id = args['vals']['PRO_PROJ_ID']
        proj_sub_lib = mainobj(mother_id)
        
        user_lib = oDB_USER.mainobj(session['sesssec']['user_id'])
        user_can_edit_folders = user_lib.has_role(db_obj, oROLE.ROLE_KEY_FOLDER_EDIT)
        user_is_role_admin    = user_lib.has_role(db_obj, oROLE.ROLE_KEY_ADMIN)

        # do access check
        if options.get('objRightsCheck',1)>=0:
            # default: do object check ...
            if mother_id == None:
                if not (GlobMethods.is_admin() or user_is_role_admin):
                    raise BlinkError(1, 'Only an Admin can create a new sub-folder in the root-folder.')
            else:
                obj_acc_matrix = table_obj_chk.get_object_rights_user(db_obj, 'PROJ', mother_id)
                if not obj_acc_matrix['insert']==1 and user_can_edit_folders:
                    raise BlinkError(2, 'You have no object-right to create a new sub-folder in this folder [ID:'+str(mother_id)+'].')

        
        # check names
        name = args['vals']['NAME']
        if proj_sub_lib.proj_name_exists(db_obj, name):
            raise BlinkError(3,'Project with name "'+name+'" already exists.')
        
        
        return super().new(db_obj, args, options)

    def del_check(self, db_obj):
        '''
        check, if project is empty
        :return [status, text]
        '''
        
        self.check_rights(db_obj, 'delete')
        
        proj_lib = mainobj(self.objid)
        sub_projs = proj_lib.sub_projects_id(db_obj)
        
        if len(sub_projs):
            return (-1, 'folder has sub folders.')

        num_docs = proj_lib.cnt_elems_of_table(db_obj, 'DOC')
        if num_docs:
            return (-2, 'folder has documents.')

        return (1, 'ok')

    def update(self, db_obj, args):
        '''
        update
        '''
        
        self.check_rights(db_obj, 'write')
        
        args['vals']['MOD_USER_ID'] = session['sesssec']['user_id']
        args['vals']['MOD_DATE'] = db_obj.Timestamp2Sql()
        return super().update(db_obj, args)
        
    def move(self, db_obj, new_mo_id):
        '''
        move object to new MOTHER
        new_mo_id can be None
        '''
        
        self.check_rights(db_obj, 'write')
        
        args = {
            'vals': {
                'PRO_PROJ_ID': new_mo_id,
            }
        }
        args['vals']['MOD_USER_ID'] = session['sesssec']['user_id']
        args['vals']['MOD_DATE'] = db_obj.Timestamp2Sql()

        return super().update(db_obj, args)