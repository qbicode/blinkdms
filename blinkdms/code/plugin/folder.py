'''
folder plugin
'''
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.obj.obj_info import Obj_info_lev2

#import blinkdms.code.lib.oPROJ.oPROJ_guisub as oPROJ_guisub
#import blinkdms.code.lib.oPROJ.oPROJ_sub as oPROJ_sub
from  blinkdms.code.lib.oPROJ   import oPROJ
#from  blinkdms.code.lib.oPROJ.oPROJ_sub import oPROJ_assoc_mod
from  blinkdms.code.lib.obj_sub import table_cls
import  blinkdms.code.lib.dict_help as dict_help
from blinkdms.code.lib.f_objhist import objhist
from blinkdms.code.lib.obj import table_obj_chk
#from blinkdms.code.lib     import oACCESS_RIGHTS
from blinkdms.code.lib.oDOC import oDOC_VERS
from blinkdms.code.lib.oVERSION import oVERSION
from blinkdms.code.lib.oDB_USER import oDB_USER
from blinkdms.code.lib import oROLE
import sys

class plug_XPL(gPlugin) :  
    '''
     * @package folder.py
     * @author  Steffen Kube (steffen@blink-dx.com)
     :var self._req_data:
       'id'  PROJ_ID
       'action': 
          'edit',
          'new',
          'del'  : delete
       'parx'  :
         'NAME'
         'NOTES'
    '''
    
    obj_acc_matrix = {} # object acc matrix

    def register(self) :
        
        table='PROJ'
        self._req_data['id'] = self._req_data.get('id',-1)  
        
        try:
            # can input any bad characters here ...
            self.objid = int(self._req_data['id'])
        except:
            self.objid = 0 # fall back
        
        db_obj  = self._db_obj1
        
        
        obj_nice = '?'
        if self.objid>=0:
            self.objlib = obj_abs(table, self.objid)
            if self.objid:
                obj_nice    = self.objlib.obj_nice_name(db_obj)
            else: 
                obj_nice    = 'root'
            #table_nice  = tab_obj.nice_name()
            
        debug.printx(__name__, "(56) PROJ-ID: " + str(self.objid))

        self.infoarr['title'] = 'folder: ' + obj_nice
        self.infoarr['title2']	= ' [ID:'+str(self.objid)+'] - single folder'

        self.infoarr['layout']	     = 'folder'
        self.infoarr['id']	     = self.objid
        self.infoarr['obj.id_check'] = -1
        self.infoarr['objtype']      = 'PROJ'
        self.infoarr['viewtype']     = 'tool'
        self.infoarr['css.scripts'] = ['x_folder.css']
        self.infoarr['objtab.acc_check'] = {
            'tab': ['read']
        }
        
        action= self._req_data.get('action','') 
        if action!='':
            self.infoarr['role.need'] = [oROLE.ROLE_KEY_FOLDER_EDIT]
            
        
        #TBD: check role rights for folder edit ...

    def act_update(self, db_obj, parx):
        
        parx['NAME']  = parx['NAME'].strip()
        parx['NOTES'] = parx['NOTES'].strip()
        
        if not len(parx['NAME']): raise ValueError ('No name set!')
        
        params = { 
            'vals': {
                'NAME' :parx['NAME'],
                'NOTES':parx['NOTES'],
                }
            }
        
        act_lib = oPROJ.modify_obj(db_obj, self.objid)
        act_lib.update(db_obj, params)
        
        self.setMessage('OK', 'Updated.')
        
    def act_new(self, db_obj, parx):
        
        parx['NAME']  = parx['NAME'].strip()
        parx['NOTES'] = parx['NOTES'].strip()
        
        if not len(parx['NAME']): raise ValueError ('No name set!')
        
        objid_use = self.objid
        if self.objid<=0:
            objid_use = None
        
        params = { 
            'vals': {
                'NAME' :parx['NAME'],
                'NOTES':parx['NOTES'],
                'PRO_PROJ_ID':objid_use,
                }
            }
        
        act_lib = oPROJ.modify_obj(db_obj)
        obj_id = act_lib.new(db_obj, params)
        
        self.setMessage('OK', 'Created.')

    def act_delete(self, db_obj):
        '''
        delete this PROJ
        '''
        
        act_lib = oPROJ.modify_obj(db_obj, self.objid)
        result = act_lib.del_check(db_obj)

        if result[0] < 1:
            raise BlinkError(1, 'Folder cannot be deleted: ' + result[1])

        act_lib.delete(db_obj)

        
    def _get_features(self, db_obj, fol_id):
        '''
        get project features + access matrix
        '''
        obj_lib_lev2 = Obj_info_lev2('PROJ', fol_id)
        self.obj_features     = obj_lib_lev2.features(db_obj) 
        self.obj_acc_matrix   = table_obj_chk.get_object_rights_user(db_obj, 'PROJ', fol_id)
        
    def _raw_tables_nice(self, tables_raw):
        new_tables=[]
        for table_loop in tables_raw:
            tablib_tmp  = table_cls(table_loop)
            nice_loop   = tablib_tmp.nice_name()
            new_tables.append( {'name': table_loop, 'nice':nice_loop } )
        return new_tables                
    
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
        self.table_acc_mx  = table_obj_chk.get_table_rights_user(db_obj, table)
        
        if fol_id>0:
            self._get_features(db_obj, fol_id)
            
            # table ACCESS matrix for this user
            self.obj_acc_mx    = table_obj_chk.get_object_rights_user(db_obj, table, self.objid) 
            
            if self.table_acc_mx['write']>0 and self.obj_acc_matrix["write"]>0:
                # checked TABLE and OBJECT rights
                self.obj_writeacc_sum = 1            
            
        else:
            self.obj_features = {}
            self.obj_acc_matrix = table_obj_chk.get_obj_acc_rights_DIS()
        
        action = self._req_data.get('action','')
        while(1):
            if action == 'edit':
                if fol_id>0:
                    self.act_update(db_obj, self._req_data['parx'])
                    self._get_features(db_obj, fol_id) # update features ...
                break
                
            if action == 'new':
                self.act_new(db_obj, self._req_data['parx'])  
                if fol_id>0:
                    # at least the modification date changes ...
                    self._get_features(db_obj, fol_id) # update features ...
                break

            if action == 'del':
                if fol_id > 0:
                    mo_id = self.obj_features['vals']['PRO_PROJ_ID']
                    self.act_delete(db_obj)

                    req_data = {
                        'mod': 'folder',
                        'id': mo_id
                    }
                    self.forward_internal_set(req_data)
                break
            
            break  # final break
    
    
        
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
        
        user_lib = oDB_USER.mainobj(session['sesssec']['user_id'])
        user_can_edit_folders = user_lib.has_role(db_obj, oROLE.ROLE_KEY_FOLDER_EDIT)
        
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
        
        menu = {}
        
        # ALLOW to insert new PROJ ?
        proj_new='disabled'
        if self.table_acc_mx['insert']>0 and self.obj_acc_matrix["insert"]>0 and user_can_edit_folders:
            proj_new = 'enabled' 
            
        if self.is_admin() or user_lib.has_role(db_obj, oROLE.ROLE_KEY_ADMIN):
            # user is admin or is 'admin'
            proj_new = 'enabled'
            
        menu['PROJ.new']=proj_new
        
        # ALLOW to EDIT PROJ ?
        proj_act = 'disabled'
        if self.table_acc_mx['insert'] > 0 and self.obj_acc_matrix["insert"] > 0 and user_can_edit_folders:
            proj_act = 'enabled'
        menu['PROJ.edit'] = proj_act
        
        # ALLOW to DEL PROJ ?
        proj_act='disabled'
        if self.table_acc_mx['delete'] > 0 and self.obj_acc_matrix["delete"] > 0 and user_can_edit_folders:
            proj_act = 'enabled' 
        menu['PROJ.del'] = proj_act
        
               

        
        """
        menu = [
      
          {'title':'folder', 'url':'', 'm_name':'folder', 'submenu': 
               [
                {'title':'new',  'url':'#NewProjDialog' },
                {'title':'edit', 'url':'#EditProjDialog' },
                {'title':'access', 'url':'' } 
               ]
          },
          {'title':'object', 'url':'', 'm_name':'object', 'submenu': 
              [ { 'title':'new', 'url':'', 'submenu':  new_tables }
              ]
          }  , 
          {'title':'select all', 'url':'', 'm_name':'object', 'submenu': 
              [ 
                {'title':'a1', 'url':''},
                {'title':'a2', 'url':''},
              ]
          }          
        ]
        """
        
        self._html.add_meta('menu', menu)        

        context = session['sesssec']['my.context']       
        doc_lib = oDOC_VERS.Table(context)
        use_table = doc_lib.table
        
        tables = ['DOC']
        proj_elems = self.proj_lib.get_objects(db_obj, tables)  # TBD:
        
       
        proj_path_arr = self.proj_lib.get_path_arr(db_obj)
        
       
        notes_tmp = None
        if 'vals' in self.obj_features:
            if dict_help.has_value( self.obj_features['vals'], 'NOTES' ):
                notes_tmp = self.obj_features['vals']['NOTES']
                #output = output + '<span style="color:gray;">' + str(self.obj_features['vals']['NOTES']) + '</span>'
                
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
            
            cntelem  = object_dict['cnt']
            objlib_tab   = table_cls(table)

            
            massdata[table]=[]

            for object_one in object_dict['elem']:
                doc_id = object_one['id']
                doc_feats = doc_lib.get_features_by_doc_id(db_obj, doc_id)
                object_one['title'] = doc_feats.get('NAME', '')
                massdata[table].append(object_one)
      
        self.sh_main_layout(massdata = massdata)  
        
      
           