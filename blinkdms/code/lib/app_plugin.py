# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
the main PLUGIN class
File:           app_plugin.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os, sys
import traceback
import html
from   flask import render_template, session
import logging

from blinkdms.conf import config
from .debug import debug
from .db import db
from .f_utilities import BlinkError, GlobMethods
from .obj_sub import table_cls, obj_abs
from .tab_abs_sql import Table_sql
from .gui.form import f_raw
from .app_plugin_ext import gPlugin_ext

# import f_module_helper

from .oDB_USER import oDB_USER



logger = logging.getLogger()

class content_IF:
    """
    content interface
    """
    _session = {} # ref to session vars
    html_content  = '' # HTML content  
    _massdata = None   # HTML Jinja var massdata
    
    def _set_session(self, session_var, infoarr):
        self._session = session_var
        self.add_meta('admin.flag', session_var['sesssec']['admin.flag'] )
        self.infoarr  = infoarr 
        
        if 'sessvars' in session_var:
            if 'head.search' in session_var['sessvars']:
                self.infoarr['head.search'] = session_var['sessvars']['head.search']
    
    def show_page(self, htmlfile):
        pass
    
    def main_layout(self, htmlfile, massdata={} ):
        pass
    def add_main_html(self, text):
        pass
    def add_meta(self, key, val):
        pass
    def forward(self, url, link_text, delay_sec=0) :
        pass

class no_html_cls(content_IF):
    def __init__(self):
        self._meta_content = {}
        self._meta_content['main'] = ''
        
        self.html_content = ''
        self._session = {}
        
    def set_content(self, content):
        self.html_content = content
        
    def meta_merge(self, meta_add):
        pass
        

class html_cls(content_IF):
    
    _session = {} # ref to session vars
    html_content  = '' # HTML content
    file_content  = '' # FILE content
    _meta_content = {} # META content, can be included by JINJA
    
    _stop_forward = 0 # if set: stop forward
    
    '''
    'forward' => forward string
    'main' : main frame HTML content
    'admin.flag' : 0,1 is admin ?
    'icon' : image in res/img
    '''
    
    def __init__(self):
        self._meta_content = {}
        self._meta_content['main'] = ''
        
        self.html_content = ''
        self._session = {}
    
    def set_file_content(self, content):
        '''
        set the FILE content; e.g. for csv export
        just use this method for the data file export, whene 'gui'=-1 is used ... !!!
        '''
        self.file_content = content
    
    def show_page(self, htmlfile):
        '''
        relative html-file (includes (chunks) ...
        '''
        debug.printx(__name__, "show_page:fullfile:"+ htmlfile +"|")
        self.html_content = render_template(htmlfile, pageinfo=self.infoarr, meta=self._meta_content, massdata=self._massdata )
    
    def add_massdata(self, massdata):
        self._massdata = massdata

    '''
    set main-frame content
    :param massdata: dict of optional mass data, e.g. in objlist
    '''    
    #def main_layout(self, htmlfile, massdata={} ):   
    #    debug.printx(__name__, "main_layout:fullfile: "+ htmlfile+"|" )
    #    self._meta_content['main'] = render_template(htmlfile, pageinfo=self.infoarr, meta=self._meta_content, massdata=massdata )
        
    
    def add_main_html(self, text):
        '''
        add content to MAIN text
        '''
        self._meta_content['main'] = self._meta_content['main'] + text + "\n"
    
    def add_meta(self, key, val):
        '''
        set met key
        if type(key==list)
           key= (var1, var2, ... )
        '''
        if type(key) == list:
            i=0
            for subkey in key:
                if not i:
                    subkey0 = subkey
                    self._meta_content[subkey] = {}
                if i==1:
                    self._meta_content[subkey0][subkey] = val
                i=i+1
        else:       
            self._meta_content[key] = val
        
    def meta_merge(self, meta_add):
        self._meta_content = {** self._meta_content, **meta_add}
        
    def setMessage(self, mess_key, message, err_stack=None ) :
        '''
        set a message, to get the message, call getErrMessage()
        mess_key: 'ERROR', 'OK', 'WARN'
        :param err_stack: real error stack
        '''
        #self.__message= {'key':mess_key, 'text':message, 'stack':err_stack}
        
        if mess_key=='ERROR':
            if err_stack is not None:
                stack_str = repr(err_stack)
            else: stack_str=''
            
            self.infoarr['err.mess'] = {'key':mess_key, 'text':message, 'stack_str':stack_str}
            
        if mess_key=='OK' or mess_key=='WARN':
            warnflag = 0
            if mess_key=='WARN': warnflag = 1
            self.infoarr['ok.mess'] = {'text':message, 'warn': warnflag}    


    def stop_forward(self, flag):
        self._stop_forward = flag

'''
 abstract plugin
 main APP PHP-page
 @var Ambiguous mod
 '''
class gPlugin:

    '''
     * set key, vals with infoarr_add()
     * @var infoarr
     *   'layout'=> 
     *        'DEFAULT'
     *        {other} : load from chunks e.g. 'home'
     *   'title' => page title
     *   'viewtype' =>
             object : single object
             list   : see also 'list.check_sel'
             tool
     *   'objtype'  => name of database table
     *   'id'       => ID of object, if 'viewtype'=='object'
         'obj.id_check' [1] : set to -1 to forbid checking for ID
         'objtab.acc_check' : dict of access check flag matrix : 
                {'tab':['read', 'write', ...], 'obj':['read', 'write', ...] }
         'menu_ext' => MENU extension: array('func') => array(array('url'=>, 'text'=>))
         'locrow'   [ {'url':'', 'text':''} ]
              url: the part after "?mod="; e.g. "obj_one&t=EXP"
         'locrow.auto': [1], - for admin area : FULL auto
                         0 (deny)
                        [2]  - reduced locrow (set title automatically)
         'locrow.show_mo' :0,1 : show mother? if 'viewtype'='object'
         'err.mess'   : {'key':mess_key, 'text':message, 'stack_str':stack_str, 'num': num of error }
         'ok.mess'    : { 'text':message, 'warn':0,1}
         'admin.only' : 0,1 allow only access for admin; see also 'admin.is'
         
         'session.need' : [OPTIONAL] module needs an active session ?
             [1] : yes, normal module ...
             -1  : does NOT an active session: e.g. 'login'          
         
         'role.need': [list of accepted role key] : the tool needs at least one of these roles
    
         'context.allow': [] of contextes: 'ACTIVE', 'EDIT' : allow this plugin context
                        - if empty: allow to everybody
        
        
         'gui'        : [1] : normal GUI framework
                        -1  : no HTML output, e.g. for an export of data, fill content with -html.set_file_content()
         'gui.cont.type' : content type ['html'] , 'file'
         'gui.cont.file' : {} of download file
            'filename' : absolute file name for download ('gui.cont.type' must be set to 'file', 'gui'=-1 )
            'name' : short name for download
         'gui.navbar.hide': 0,1 OPTIONAL
         'list.check_sel' : [0] - for 'viewtype'='list'
               1: check, if an object was selected, if not: error
               
         'js.scripts' : DEPRECATED! list of js scripts in res/js
         'css.scripts': DEPRECATED! list of css scripts in res/css     
    -- PRODUCED vars:
         'context'  : self._sessi['sesssec']['my.context']
         'user.fullname'  : added by _init()
         'user.roles' : all roles of user
         'mod'        : added by __init__
         'table.nice' : added by _check_inits, if 'objtype' given
         'admin.is'   : 0,1 user is admin? will be set by this class, only used for HTML-pages
       if 'viewtype'=='object' (and 'id' given)
         'obj.nice'   : nice object name
         'obj.list.table' : give alternative table for object list
       -----
          'head.search' : added by html_cls._set_session()
          'head.sea.tables' : search tables { 
           'tabs': [[table_RAW, table_nice]], list of tables ...
           'set': sess_table 
           }
            
    '''
    infoarr  = {}
    _session = {} # ref to session vars

    _req_data = {}
    '''
    # request data from web REQUEST
    ['__FILES__'] list of files
    '''
    _req_data_new = {} # used paramas for _forward
    _forward = 0  # do a complete internal forward of the plugin ? prevents performing of mainframe()
    '''
    - set also  self._req_data_new for new input params
    - the forward will be called after startMain()
    '''
    
    _superglobal = None
    __rpclib  = None # JSONRPC object
    _db_obj1  = None # first  DB object
    _db_obj2  = None # second DB object
    _db_obj3  = None # third  DB object

    _html = None
    _obj  = None     # class fOBJ_subs
    #__message = {}   # error message
    _mod   = ''       # module name
    _mod_is_adm_space = 0  # module is on ADMIN space ?
    _do_restart = 0  
    '''
    - after UPDATE of object do restart ?
    - this preserves e.g. the self.infoarr['err.mess']
    - rerun ....:
       _check_inits() 
       startMain()
    '''
   
    
    objlib = None    # single object lib 
    _is_rest = 0     # this is a rest call?
    _rest_data = None # data for REST interface

    '''
     * TBD: NOT used!
     * @var array _obj_data
    '''
    _obj_data = {}
    
    objid = None # the object ID
    
    def __init__(self, db_obj1, mod):
        '''
        :param db_obj1: database object
        '''
        self._db_obj1 = db_obj1
        self._db_obj2 = None
        self.infoarr  = {}
        self._output_buffer = ''
        self._mod     = mod
        self._mod_is_adm_space = 0
        self._do_restart       = 0
        self._req_data_new = {}
        self._forward = 0
        self.objid  = None
        
        mod_parts     = mod.split('/')
        if mod_parts[0]=='ADM':
            # automatic ADM-modules 
            self.infoarr['admin.only'] = 1
            self._mod_is_adm_space     = 1
        
        self.infoarr['mod'] = self._mod
   

        # TBD: remove this ...self.gPlugExt = gPlugin_x(self.infoarr, xopt)
    
    def route(self, db_obj):
        '''
        forward to other Plugin, before call
        return:
         'mod' : name of new module
         'infoarr': new settings for forward module
           'layout': ... (CHANGED:2020-04-19)
        '''
        return {}
        
    def register(self) :    
        pass

    def startMain(self) :  
        pass
    
    @property
    def restart(self):
        return self._do_restart 
    
    @restart.setter
    def restart(self, flag):
        self._do_restart = flag  
        
    # this is a rest call ?
    @property
    def is_rest(self):
        return self._is_rest 
    @is_rest.setter
    def is_rest(self, flag):
        self._is_rest = flag
        
    @property
    def rest_data(self):
        return self._rest_data 
    @rest_data.setter
    def rest_data(self, data):
        self._rest_data = data 
        
    @property
    def forward(self):
        return self._forward
    
    @property
    def req_data_new(self):
        return self._req_data_new
        
    def forward_internal_set(self, req_data):
        # activate internal forward
        # this flag prevents performing the mainframe() method
        self._req_data_new = req_data
        self._forward = 1        
    
    def _init(self):
        '''
        init class internal
        '''        
        
        self._html = html_cls()
        # OLD: 
        #if self.infoarr.get('gui',1) > 0:
             #self._html = html_cls()
        #else:
            #self._html = no_html_cls() # e.g. export csv or images
            
        self._html._set_session(self._session, self.infoarr)

        self.plugin_ext_lib = gPlugin_ext(self._html, self.infoarr, self._mod_is_adm_space)

        

        #TBD: self._obj  = fOBJ_subs()

    def _set_error_page(self):
        # an severe error occurred, set the ERROR page
        self.infoarr['layout'] = 'error'

   
    
    '''
     * check initial settings like self.infoarr
     * - get initial data for object from database
     * set add_meta 'table'
     * set add_meta 'id'
     * @throws Exception
     '''
    def _check_inits(self) :

        table_nice  = '?'
        # table_name  = ''
        self.objlib = None
        

        context = self._session['sesssec'].get('my.context', '')
        locrow_auto = self.infoarr.get('locrow.use', 0)
            
        prefix=''
        if self._mod_is_adm_space:
            prefix = 'ADM/'
            locrow_auto = 1
        
        # LOCATION LIST
        if 'locrow' not in self.infoarr:
            self.infoarr['locrow'] = []         
        
        if 'objtype' in self.infoarr:
            # check tablename ...
            if self.infoarr['objtype']=='' :
                raise BlinkError(1, 'No tablename given!')
            
                          
           
            tablename  = self.infoarr['objtype'] 
            tablib     = table_cls(tablename)
            table_is_real = 1
            
            table_nice = tablib.nice_name()
            self.infoarr['table.nice'] = table_nice
            

            
            self._html.add_meta('table', tablename )
                       
            
            icon = 'o.' + tablename + '.svg'
            self.infoarr['icon']= icon

            objid      = None

            if 'id' in self.infoarr:
                
                do_id_check = 1
                if self.infoarr.get('obj.id_check',1)<0:
                    do_id_check = 0
                
                if do_id_check:
                    # check id
                    objid = self.infoarr['id']
                    if not objid:
                        raise BlinkError(4, 'No ID of object given.')
     
                    self.objid = objid
            
            self.plugin_ext_lib.set_object(tablename, self.objid)
            self.plugin_ext_lib.sec_check_obj(self._db_obj1)
 
            if self.infoarr.get('viewtype','') == 'object' :
                #
                # single object 
                #

                if not objid:
                    self.infoarr['title']  = 'table: '+ table_nice
                    raise BlinkError(5, 'No ID for object given.')
                
                
                self.objlib = obj_abs(tablename, objid)  
                
                if not self.objlib.obj_exists(self._db_obj1):
                    raise BlinkError(6, 'Object with ID: '+str(objid)+' does not exist.')
                
                # if this is a business object ...
                # SECURITY: check access rights only for the HUBE application ...   



                self._html.add_meta('id', objid )  
                obj_nice  = self.objlib.obj_nice_name(self._db_obj1)

                self.infoarr['obj.nice'] = obj_nice
                
                
                self._obj_data = None

                if not self._mod_is_adm_space and tablename == 'VERSION':

                    doc_id = self.objlib.main_feat_val(self._db_obj1, 'DOC_ID')
                    doc_lib = obj_abs('DOC', doc_id)
                    doc_code = doc_lib.main_feat_val(self._db_obj1, 'C_ID')
                    self.infoarr['title'] = self.infoarr['title'] + ' [' + doc_code + ']'

                    if self.infoarr.get('locrow.show_mo', 0):
                        if context == 'EDIT':
                            doc_link = 'doc_edit'
                        if context == 'ACTIVE':
                            doc_link = 'doc_view'

                        self.infoarr['locrow'].append({'url': doc_link + '&id=' + str(objid), 'text': 'document'})
                
                if locrow_auto>0:  
                    
                    if self.infoarr.get('obj.list.table','') != '':
                        # alternative table for list view
                        tablename_list  = self.infoarr['obj.list.table']
                        #tablist_lib      = table_cls(tablename_list)
                        #table_list_nice = tablist_lib.nice_name()
                    else:
                        tablename_list = tablename
                        #table_list_nice = table_nice
                        
                    self.infoarr['locrow'].append( {'url': prefix+'obj_list&t='+tablename, 'text':  'list of '+ table_nice } )
                
                if self._mod=='ADM/obj_one' or self._mod=='obj_one':
                    self.infoarr['title'] = obj_nice
                    self.infoarr['title2']   = '[ID:'+str(objid)+']' + ' - single object of type: ' + table_nice                    
                    
                    pass
                else:  
                    if locrow_auto>0:   
                        self.infoarr['locrow'].append( {'url': prefix + 'obj_one' + '&t=' + tablename + '&id=' + str(objid), 'text': obj_nice} )
                                  


            if self.infoarr.get('viewtype','') == 'list' :
                
                if self._mod=='ADM/obj_list':
                    self.infoarr['title'] = 'list of '+ table_nice
                else:
                    if locrow_auto>0:   
                        self.infoarr['locrow'].append( {'url': prefix + 'obj_list&t='+tablename, 'text':  'list of '+ table_nice  } )
                
                if self.infoarr.get('list.check_sel', 0):
                    '''
                    check, if objects were selected
                    '''
                    sql_select_lib = Table_sql(tablename)
                    if not sql_select_lib.filter_is_active():
                        raise BlinkError(14, 'A filter for this table must be active to use this plugin.')
       
            
        # append yourself if locrow_auto==1
        if locrow_auto==1:   
            url = self._mod
            if len(self.infoarr.get('objtype','')):
                url = url+'&t='+ self.infoarr['objtype']
            if self.objid is not None and self.objid != '':
                url = url + '&id=' + str(self.objid)
            #FUTURE: put url to url-param
            self.infoarr['locrow'].append({'url': url, 'text': self.infoarr['title']})
            
        #
        # do ACCESS check of the module 
        #
        if self._session['sesssec']['admin.flag']:
            self.infoarr['admin.is'] = 1
            
        else:
            # user is NOT admin
            accept_roles = self.infoarr.get('role.need', [])
            needs_content_admin = 0
            is_content_admin = 0
            
            tmp_user_roles = self.infoarr.get('user.roles',[])
            
            if 'admin' in tmp_user_roles:
                is_content_admin = 1

            if 'admin' in accept_roles:
                needs_content_admin = 1
                
            # analyse roles, if rewquired
            if len(accept_roles):
                found_role=0
                for need_role in accept_roles:
                    if need_role in tmp_user_roles:
                        found_role=1
                if not found_role:
                    raise BlinkError(17, 'You must have role "'+need_role+'" perform this tool.')
                
            if self.infoarr.get('admin.only', 0) > 0:
                
                #debug.printx( __name__, '(582): admin.only?  needs_content_admin:' + str( needs_content_admin ) + \
                #    ' is_content_admin:' + str( is_content_admin ) + ' roles: ' + str(self.infoarr.get('user.roles',[]))         
                #              )
                
                if needs_content_admin and is_content_admin:
                    pass  # this module is allowed
                else:
                    raise BlinkError(15, 'You must be admin to perform this tool.')
            
            if len(self.infoarr.get('context.allow',[])):
                # check right context
                if self._session['sesssec'].get('my.context','') not in self.infoarr['context.allow']:
                    self._set_error_page() # severe error
                    raise BlinkError(16, 'You can not use this tool in the '+ self._session['sesssec'].get('my.context','') +' context.')             


    def _set_Superglobal(self, db_obj, superglobal ) :
        """
        set superglobal vars and othe rbasic variables
        """
        self._superglobal = superglobal
        
        self.infoarr['site.title']     = self._superglobal['site.title']
        self.infoarr['system.company'] = self._superglobal['system.company']
        
        if db_obj:
            # after valid login ...
        
            if self._session['sesssec'].get('my.mdo_grp_id', 0):
                tmp_id  = self._session['sesssec']['my.mdo_grp_id']
                obj_lib = obj_abs('USER_GROUP', tmp_id)
                self.infoarr['mdo_grp.name'] = obj_lib.obj_nice_name(db_obj)
                
            if self._session['sesssec'].get('my.ser_grp_id', 0):
                tmp_id  = self._session['sesssec']['my.ser_grp_id']
                obj_lib = obj_abs('USER_GROUP', tmp_id)
                self.infoarr['ser_grp.name'] = obj_lib.obj_nice_name(db_obj)            
           
            
        

    def _set_req_data(self, req_data):
        '''
        set and REPAIR req_data
        '''
        
        f_raw.post_dict_repair(req_data)  
        
        self._req_data = req_data
        
        # WARNING: if activate this debug, it can show passwords!
        # debug.printx( __name__, 'REQ_DATA: ' + str( self._req_data ) )
     
    def _set_session(self, session_var, mod_session_need):
        """
        init also other vars
        :param mod_session_need: int 0,1
        """
        self._session = session_var
        
        # init other infoarr things
        if mod_session_need > 0: # normal module ?
            user_id = self._session['sesssec']['user_id']
            user_lib = oDB_USER.mainobj(user_id)
            self.infoarr['user.fullname'] = user_lib.get_fullname(self._db_obj1)
            self.infoarr['user.sign'] = session['sesssec'].get('user.sign','?')
            self.infoarr['context'] = self._session['sesssec']['my.context']
            self.infoarr['user.roles'] = user_lib.get_roles(self._db_obj1)

            if 'roles' in session['sesssec']:
                if 'edit' in session['sesssec']['roles']:
                    self.infoarr['mainmenu.sh.EDIT'] = 1
           
            
    def infoarr_add(self, key, val):
        self.infoarr[key] = val
        
    def infoarr_post( self, key, val ):
        '''
        modify infoarr after methode _check_inits
        '''
        
        if key=='obj.list.table':
            #
            # replace ELEMENT 0 of infoarr['locrow']
            #
            if len(self.infoarr['locrow'])<1:
                return # not a valid number of rows ...
            
            replace_index = 0
            
            tablename=val
            tablist_lib     = table_cls(tablename)
            table_list_nice = tablist_lib.nice_name()            
            self.infoarr['locrow'][replace_index] = {'url': 'obj_list&t='+tablename, 'text':  'list of '+ table_list_nice }    
    
    def is_admin(self):
        return GlobMethods.is_admin()
        
    def db_obj2(self):
        """
        get DB object No 2
        """
        if self._db_obj2 is None:
            access_config = self._session['sesssec']['dbacc']
            self._db_obj2 = db()
            self._db_obj2.open( access_config )
        
        return self._db_obj2
    
    def db_obj3(self):
        """
        get DB object No 3
        """
        if self._db_obj3 is None:
            access_config = self._session['sesssec']['dbacc']
            self._db_obj3 = db()
            self._db_obj3.open( access_config )
        
        return self._db_obj3    
        
    '''
     * show a global VARIABLE from  self._superglobal
     * @param unknown key
     * @return None
     '''
    def get_globalfeat(self, key) :

        val = None
        while True:

            #default:
            if key in self._superglobal :
                val = self._superglobal[key]
            break

        return val
    
    def plug_url(self):
        """
        get plugin-URL
        """
        return '?mod=' + self._mod

    def x_get_html_content(self):
        # for start.py
        return self._html.html_content
    
    def x_get_file_content(self):
        # for start.py
        return self._html.file_content    

    '''
     * get a LOCAL VARIABLE from  this class
     * @param string key
     * @return variant
     '''
    def _g_feature(self, key) :

        val = None
        while True:
            
            if key ==  'menu_ext':
                if 'menu_ext' in self.infoarr and len(self.infoarr['menu_ext']) :
                    val = self.infoarr['menu_ext']
                break
            break
        return val


   

   


    '''
    produces the Output for the HTML page
    - not performed if self._forward = 1
    '''
    def mainframe(self):
        pass


    def _check_adm_file(self, shortname):
        '''
        check for "ADM/"
        :return: [shortname, is_admin_flag]
        '''
        
        if len(shortname)<=4:
            return [shortname, 0]
        
        if shortname[0:4]=='ADM/':
            newname = shortname[4:]
            return [newname, 1]
        
        return [shortname, 0]   

    def _getChunkFile(self, name) :
        '''
        :param name: chunk-file-short name; e.g. 'obj_one' or 'ADM/g_info'
        :return 
          0: FULL name
          1 'chunks/htmlfile.html'
        '''

        [name, is_admin_flag] = self._check_adm_file(name)
        
        htmlfile = name +'.html'
        if is_admin_flag:
            htmlfile_short = os.path.join('ADM', htmlfile)
        else:
            htmlfile_short = htmlfile
        htmlfile_full  = os.path.join( self._superglobal['app.templates']  , htmlfile_short )
            
        if ( not os.path.exists(htmlfile_full)) :
            raise ValueError('_getChunkFile "' + htmlfile_full + '" failed')

        return [htmlfile_full, htmlfile_short]
    
    def _getChunkFile_short(self,name):
        (htmlfile_full, htmlfile_short) = self._getChunkFile(name) # just do the test
        htmlfile = htmlfile_short   #OLD: 'chunks/'+ name +'.html'
        return htmlfile
    
    def log_err(self, message, err_num=0, err_stack=None ):
        # log error to logger 
        
        if err_stack is not None:
            stack_str  = str(repr(err_stack))
            # debug.printx(__name__,  "(686) setMessage:ERR:STACK " + stack_str)
        else: 
            stack_str='MOD:'+ self._mod
        
        log_extra=''
        if err_num:
            log_extra = log_extra + '; (ERRNUM:' + str(err_num) +')'
        if self.infoarr.get('objtype','') and self.objid:
            # extra logging context
            log_extra = log_extra + '; OBJ:t:'+self.infoarr['objtype']+',id:'+str(self.objid)
        
        logger.error( message + log_extra, extra={ 'user': session['sesssec'].get('user',''), 'err_stack':stack_str } ) 
        
        return { 'stack_str': stack_str }

    def setMessage(self, mess_key, message, err_num=0, err_stack=None ) :
        '''
        set a message and log error to logger 
        mess_key: 'ERROR', 'OK', 'WARN'
        '''

        if mess_key=='ERROR':
            log_info = self.log_err( message, err_num, err_stack )
            self.infoarr['err.mess'] = {'key':mess_key, 'text':message, 'stack_str': log_info['stack_str'], 'num':err_num }
            
        if mess_key=='OK' or mess_key=='WARN':
            warnflag = 0
            if mess_key=='WARN': warnflag = 1
            self.infoarr['ok.mess'] = {'text':message, 'warn': warnflag}
            
    def getErrMessage(self):
        # get last Error message: DICT
        if 'err.mess' in self.infoarr:
            return self.infoarr['err.mess']
        else:
            return None     
        
    def exception_message(self, exc ) :
        '''
        - handle an Exception, call setMessage()
        - write error to log
        usage:
        --------
        except Exception as exc:
            self.exception_message(exc)
        '''
        
        message = str(exc)
        exc_type, exc_value, exc_traceback = sys.exc_info() 
        err_stack = traceback.extract_tb(exc_traceback)
        debug.printx(__name__, "ERROR: exc_type:"+ str(exc_type) )
        debug.printx(__name__, "exc_value:"+ str(exc_value) )
        debug.printx(__name__, "exc_traceback:"+ repr(err_stack) )       
        
        self.setMessage('ERROR', message)   
        
    def exception_log( self, exc, message_extra='' ) :
        # log exception to logger
        
        err_stack = traceback.extract_tb( exc.__traceback__ )
        message  = str(exc)
        err_num  = 0
        
        if message_extra!='':
            message = message_extra + '; ORI:'+ message
        self.log_err( message, err_num, err_stack )

   

    def sh_main_layout( self, massdata={} ) :
        '''
        save massdata in cache ...
        '''
        
        #if self.infoarr.get('layout','') != ''  :
        #    raise BlinkError(906,'LAYOUT missing.')
        #module = self.infoarr['layout']
        #htmlfile = self._getChunkFile_short(module)
        #self._html.main_layout(htmlfile, massdata=massdata)
        
        self._html.add_massdata(massdata)
        

    def html_add(self, text, endline="\n", escape=0):
        '''
        :param escape: if 1: html.escape()
        '''
        if type(text) != str: 
            text = str(text)
            
        if escape:
            text = html.escape(text)
        self._output_buffer = self._output_buffer + text  + endline
        
    def html_get(self):
        return self._output_buffer
    

    def show_page(self) :
        """
        show page, template defined in self.infoarr['layout']
        handles also Admin-Pages: e.g. "ADM/home"
        """

        if self._db_obj1 is not None:
            # insert standard data e.g. for the header-box
            self.plugin_ext_lib.post_actions(self._db_obj1)
        
        html_super_short=self.infoarr['layout']
        
        if html_super_short.startswith('ADM'):
            html_super_short = html_super_short[4:]
            htmlfile = os.path.join('ADM', html_super_short + '.html')
        else:
            htmlfile = os.path.join(html_super_short + '.html')
            
        htmlfile_full =  os.path.join(  self._superglobal['app.templates'],  htmlfile ) # (CHANGED:2020-04-19)
        if not os.path.exists(htmlfile_full) :
            err_tmp = "Template: " + htmlfile_full +" not exists."
            debug.printx(__name__,  "ERR: "+err_tmp)
            
            self.setMessage('ERROR', "Template '"+htmlfile+"' not found" )
            htmlfile = 'chunks/error.html'
       
        
        self._html.show_page(htmlfile) 

        
    def content_is_file(self):
        if  self.infoarr.get('gui.cont.type','html')=='file':
            return 1
        else:
            return 0

    def content_down_file(self):
        # get file-info, if set
        # :return: dict 
        file_info = self.infoarr.get('gui.cont.file',{})
        return file_info
    
