'''
folder select plugin
'''
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.obj.obj_info import Obj_info_lev2

import  blinkdms.code.lib.dict_help as dict_help
from  blinkdms.code.lib.oPROJ    import oPROJ
from blinkdms.code.lib.f_objhist import objhist
from blinkdms.code.lib.oDOC      import oDOC_VERS
from blinkdms.code.lib.oDB_USER  import oDB_USER
from blinkdms.code.lib import oROLE

import sys

class plug_XPL(gPlugin) :  
    '''
     * @package folder.py
     * @author  Steffen Kube (steffen@blink-dx.com)
     :var self._req_data:
       'id' : can be 0 for ROOT
       'action' : 'select' ==> do forward
       'back_key' : keyword to return
           'DOC.new'
    '''
    

    def register(self) :
        
        table='PROJ'
        self._req_data['id'] = self._req_data.get('id',0)
         
        self.objid = int(self._req_data['id'])
        db_obj  = self._db_obj1
        
        
        obj_nice = '?'
        if self.objid>=0:
            self.objlib = obj_abs(table, self.objid)
            if self.objid:
                obj_nice    = self.objlib.obj_nice_name(db_obj)
            else: 
                obj_nice    = 'root'

        self.infoarr['title'] = 'create document : select folder'
        self.infoarr['title2']	= ' [ID:'+str(self.objid)+'] - select folder'
        self.infoarr['layout']	     = 'folder_sel'
        self.infoarr['id']	     = self.objid
        self.infoarr['obj.id_check'] = -1
        self.infoarr['objtype']      = 'PROJ'
        self.infoarr['viewtype']     = 'tool'
        self.infoarr['css.scripts'] = ['x_folder.css']
        self.infoarr['objtab.acc_check'] = {
            'tab': ['read']
        }

    def _get_features(self, db_obj, fol_id):
        '''
        get project features + access matrix
        '''
        obj_lib_lev2      = Obj_info_lev2('PROJ', fol_id)
        self.obj_features = obj_lib_lev2.features(db_obj) 
      
    
    def startMain(self) :
        
        table='PROJ'
        db_obj = self._db_obj1
        fol_id = self.objid
    
        self.tablib  = table_cls('PROJ')
        obj_lib      = obj_abs('PROJ', fol_id)
        self.obj_writeacc_sum = 0
        
        if fol_id>0:
            # check if exists, do not for ROOT ...
            if not obj_lib.obj_exists(db_obj):
                raise ValueError ('Folder with ID:'+str(fol_id)+' not found.')
        
        self.proj_lib = oPROJ.mainobj(fol_id) 
        
        if fol_id>0:
            self._get_features(db_obj, fol_id)
            
        else:
            self.obj_features = {}
           
        action = self._req_data.get('action','')
        
        if action == 'select' and fol_id>0:
            
            # forward to doc.new ...
            req_data = {
                'mod':     'doc_new',
                'proj_id': fol_id
            }
            self.forward_internal_set(req_data)
            return            
        
    
        
    def mainframe(self):
        '''
        post to HTML ...
          'meta':
             proj.id
             proj.path : pute HTML ...
             ['menu']
               ['new_tables'] 
               ['PROJ.new'] = 'enable' |  ['disable']
        '''
        
        db_obj = self._db_obj1
        fol_id = self.objid
        
        objhist_lib = objhist()
        objhist_lib.check_obj('PROJ', self.objid)
        info_struct = {}
            
        if 'vals' in self.obj_features:
            self._html.add_meta('proj.name' , self.obj_features['vals']['NAME'])
            self._html.add_meta('proj.notes', self.obj_features['vals']['NOTES'])

            user_tmp = self.obj_features['vals']['DB_USER_ID']
            if user_tmp:
                info_struct['crea_user'] = oDB_USER.Table.get_fullname(db_obj, user_tmp)
            user_tmp = self.obj_features['vals']['MOD_USER_ID']
            if user_tmp:
                info_struct['mod_user'] = oDB_USER.Table.get_fullname(db_obj, user_tmp)

            tmp_date = str(self.obj_features['vals']['CREA_DATE'])
            info_struct['crea_date'] = tmp_date[0:10]

            if self.obj_features['vals']['MOD_DATE'] != None:
                tmp_date = str(self.obj_features['vals']['MOD_DATE'])
                info_struct['mod_date'] = tmp_date[0:10]
            
        else:
            self._html.add_meta('proj.name' , '')
            self._html.add_meta('proj.notes', '')


        self._html.add_meta('info', info_struct)
        self._html.add_meta('proj.id', fol_id)
        self._html.add_meta('proj.form.mod_key', self._req_data['back_key'] ) 
        

        context = session['sesssec']['my.context']       
        doc_lib = oDOC_VERS.Table(context)
        #use_table = doc_lib.table
        
        tables = ['DOC']
        proj_elems = self.proj_lib.get_objects(db_obj, tables)  # TBD:
        
       
        proj_path_arr = self.proj_lib.get_path_arr(db_obj)
        
       
        notes_tmp = None
        if 'vals' in self.obj_features:
            if dict_help.has_value( self.obj_features['vals'], 'NOTES' ):
                notes_tmp = self.obj_features['vals']['NOTES']
                
        self._html.add_meta('proj.path', proj_path_arr)  
        self._html.add_meta('proj.notes', notes_tmp)  

        parent_id = self.proj_lib.getParentProj(db_obj)
        self._html.add_meta('parent_id', parent_id)  
             
        massdata={}  

        object_dict  = proj_elems['PROJ_ORI']
        massdata['PROJ_ORI']=[]
        for proj in object_dict['elem']:
            massdata['PROJ_ORI'].append(proj)
            
        for table, object_dict in proj_elems.items() :

            if (table=='PROJ_ORI') :
                continue
            
            #cntelem  = object_dict['cnt']
            #objlib_tab   = table_cls(table)
            
            massdata[table]=[]

            for object_one in object_dict['elem']:
                doc_id = object_one['id']
                doc_feats = doc_lib.get_features_by_doc_id(db_obj, doc_id)
                object_one['title'] = doc_feats.get('NAME', '')
                massdata[table].append(object_one)
      
        self.sh_main_layout(massdata = massdata)  
        
      
           