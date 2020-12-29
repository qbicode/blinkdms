# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
start script for FLASK
File:           start.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""

import os, sys
import traceback
import time
import json
import logging
import urllib

import importlib
from flask import request, send_from_directory, send_file
from flask import Flask, session, redirect, Response
from flask_session import Session  # use flask_session (is undocumented!)
from flask import jsonify
from flask_mail import Mail

# from jsonrpcserver import method, dispatch

from jinja2.exceptions import TemplateSyntaxError

from blinkdms.conf import config
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.db import db
from blinkdms.code.lib.f_utilities import BlinkError




# root_path = config.superglobal['gui.root_dir']+'/'
app = Flask(__name__, static_folder='static',
            template_folder='templates')  # config the STATIC, TEMPLATES dirs
app.secret_key = 'xvcvqwbn29'  # secret key for SESSION

SESSION_TYPE     = 'filesystem' # or redis
SESSION_FILE_DIR = '/tmp/blk_ses'
#SESSION_FILE_THRESHOLD=500
#SESSION_FILE_MODE
SESSION_PERMANENT  = False
SESSION_KEY_PREFIX = 'blkdms:'
PERMANENT_SESSION_LIFETIME = 60*120   # 2 hours

# email server, due to miguelgrinberg.com
MAIL_SERVER = 'localhost'
MAIL_USE_TLS = False
MAIL_USE_SSL = False

app.config.from_object(__name__)

# enable jinja2 extensions - i.e. continue in for loops
app.jinja_env.add_extension('jinja2.ext.do')

mail = Mail(app) # due to miguelgrinberg.com

sess = Session()
sess.init_app(app)

try:
    logger = logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s\t%(levelname)s\t%(pathname)s:%(lineno)d\t%(user)s\t%(message)s\t%(err_stack)s',
        level=logging.DEBUG,
        filename='/var/log/blinkdms/main.log',
    )
    
except:
    pass

class page_org:
    
    page_lib = None
    
    def __init__(self):
        self.page_lib = None
    
    def _show_page(self):
        self.page_lib.show_page()
    
    def forward(self):
        # do an INTERNAL forward ?
        if not self.page_lib.forward:
            return 0
        
        if self.page_lib.getErrMessage():
            # an error occured, do NOT forward ...
            return 0
        
        return 1
    

    def forward_get_req(self):
        # get new req_data
        if not self.page_lib.forward:
            return 0
        
        return self.page_lib.req_data_new
    
   

    def show_error(self,message, err_stack) :

        mod='error'
        self.page_lib.setMessage('ERROR', message, err_stack)
        self.page_lib.infoarr_add('layout', mod)
        self.page_lib.show_page()

    def _get_plug_file_info(self, module):
        '''
        create import path and full plugin-file name
        :param string module: e.g. "login" or root/terminal"
        '''

        mod_parts     = module.split('/')
        if mod_parts[0]=='ADM':
            # admin plugin
            del( mod_parts[0] ) # remove the "ADM" string element
            plugin_dir     = 'ADM/plugin/'
            plugin_py_path = 'blinkdms.ADM.plugin.'
            cfgname        = module[4:] + '.py' # remove ADM/ ...
        else:
            plugin_dir = 'code/plugin/'  # calculate dynamic directory OLD: 'code/plugin/'
            plugin_py_path = 'blinkdms.code.plugin.'
            cfgname        = module + '.py'

        
        cfgname_full= plugin_dir + cfgname
        if not os.path.exists(cfgname_full) :#
            debug.printx(__name__, "ERROR: Modul not found: "+ cfgname_full )
            raise ValueError ('Module "'+ module +'" not found')
        
        # check for sub dirs
       
        import_substr = '.'.join(mod_parts)
        
        imppath = plugin_py_path + import_substr  # old: 'blinkdms.code.plugin.'
        
        return {'imppath':imppath, 'file':cfgname_full}

    def _get_import_path(self, req_data, mod):
        try:
            plug_info = self._get_plug_file_info(mod)
        except:
            old_mod = mod
            mod = 'error'
            plug_info = self._get_plug_file_info(mod)
            self.cached_error.append( {'key':'ERROR', 'txt': 'Plugin "' + old_mod + '" not found.'} )
        req_data['mod'] = mod   # update mod ...
        
        import_string = plug_info['imppath']
        debug.printx(__name__, "import_plugin: "+ import_string )  
        return import_string

    def _reset_sess_vars(self):
        session['loggedin'] = 0
        if not 'sesssec' in session:
            session['sesssec'] = {}                
        session['sesssec']['admin.flag'] = 0        

    def get_content(self):
        # HTML or file content
        if self.page_lib.infoarr.get('gui',1)>0:
            return self.page_lib.x_get_html_content()
        else:
            # download file ...
            return self.page_lib.x_get_file_content()
    
    def start_page(self, mod, req_data, superglobal):
        '''
        - if SESSION not active : call 'login' preserve old 'mod' in req_data['old_mod']
        :param string mod: e.g. "login" or root/terminal"
        
        '''

        superglobal['app.path.root'] = os.path.dirname(__file__)
        superglobal['app.templates'] = os.path.join(superglobal['app.path.root'], 'templates')
        
        self.cached_error = []
        db_obj1 = None # database object
        
        # set this initially ...
        if 'loggedin' not in session:
            
            self._reset_sess_vars()
            if mod =='logout':
                # session is already dead ...
                mod='login'
        
        mod_session_need = 1
        mods_without_session = ['login', 'p_reset']
        if mod in mods_without_session:
            mod_session_need = 0
            self._reset_sess_vars()             
        
        if mod_session_need:
            # normal module ...
            # check session
            if session.get('loggedin', 0) <= 0:

                req_data['old_mod'] = mod
                mod='login'
                self._reset_sess_vars()
                mod_session_need = 0   # switch to "no need"
            
            if 'loggedin' in session and session['loggedin']>0:
                access_config = session['sesssec']['dbacc']
                db_obj1 = db()
                db_obj1.open( access_config )

        
        # POST module routing ...
        if mod=='obj_one' and req_data['t']=='PROJ':
            mod='folder' #TBD: remove this in future ...
        
        import_string = self._get_import_path(req_data, mod)
        imported_mod = importlib.import_module(import_string)
        self.page_lib = imported_mod.plug_XPL(db_obj1, mod)   # FACTORY of class gPlugin()
        
        route_params = {}
        if len(self.page_lib.route(db_obj1)):
            # a module can route to an other module ...
            route_params = self.page_lib.route(db_obj1)
            newmod = route_params['mod']
            mod    = newmod
            debug.printx( __name__, 'ROUTE_to:' + newmod+ ' PARAMS:'+ str(route_params) )
            import_string = self._get_import_path(req_data, mod)
            imported_mod = importlib.import_module(import_string)
            self.page_lib = imported_mod.plug_XPL(db_obj1, mod)              
        
        debug.printx( __name__, 'mod: '+mod+ ' need_session:'+ str(mod_session_need) )
        
        self.page_lib._set_session(session, mod_session_need)
        self.page_lib._set_Superglobal(db_obj1, superglobal)
        self.page_lib._set_req_data(req_data)
    
        self.page_lib.register()
        if 'infoarr' in route_params:
            # update infoarr after routing
            self.page_lib.infoarr = {**self.page_lib.infoarr, **route_params['infoarr'] } 
            debug.printx( __name__, 'ROUTE_to:infoarr: '+ str(self.page_lib.infoarr) )
            
        self.page_lib._init()

        if len(self.cached_error) :
            self.page_lib.setMessage(self.cached_error[0]['key'], self.cached_error[0]['txt'])


        stop      = 0
        error_got = 0
        err_num   = 0
        showpage  = 1 # show the HTML content ?
        
        try :
            self.page_lib._check_inits() 
            self.page_lib.startMain()
            if self.page_lib.forward:
                # do NOT perform mainframe()
                showpage = 0
                pass
            else:
                if self.page_lib.restart:
                    # rerun INIT and startMain (after updates)
                    self.page_lib._check_inits() 
                    self.page_lib.startMain()
                    
                self.page_lib.mainframe()  # fill the main frame with content ...
            
        except  TemplateSyntaxError as exc:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = '{0}:{1} error: {2}'.format(exc.filename, exc.lineno, exc.message)
            debug.printx(__name__, "JINJA:"+ message )
            
            error_got=1
        except BlinkError as err_obj:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            message = str(exc_value) 
            err_num = err_obj.errnum
            error_got = 1        
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            message = str(exc_value) 
            error_got = 1

        show_err_page = 0
        if error_got:
            
            err_stack = traceback.extract_tb(exc_traceback)
            debug.printx(__name__, "START_PAGE: exc_type:"+ str(exc_type) )
            debug.printx(__name__, "exc_value:"+ str(exc_value) )
            debug.printx(__name__, "exc_traceback:"+ repr(err_stack) ) 


            self.page_lib.setMessage('ERROR', message, err_num=err_num, err_stack=err_stack)
            if showpage:
                show_err_page = 1
                showpage = 0
        
        if showpage:

            try :
                page_config = self.page_lib.infoarr
                if 'layout' not in page_config :
                    #self.page_lib.infoarr['layout']='home'
                    raise BlinkError(302, 'LAYOUT missing in page config.')

                self._show_page()

            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                message = str(exc_value) + ' STACK: ' + str(exc_traceback)
                err_stack = traceback.extract_tb(exc_traceback)
                
                debug.printx(__name__, "SHOW_PAGE: exc_type:"+ str(exc_type) )
                debug.printx(__name__, "exc_value:"+ str(exc_value) )
                debug.printx(__name__, "exc_traceback:"+ repr(err_stack) )
                self.show_error(message, err_stack)

        if show_err_page:
            
            mod = 'error'
            if not session.get('loggedin', 0):
                mod = 'login'
            
            self.page_lib.infoarr_add('layout', mod)
            self.page_lib.show_page()


     
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response  


@app.route("/api/rest", methods=["POST", "GET"])
def restapi():
    '''
    REST ..
    '''

    from blinkdms.code.api import rest
    allow_without_sess = ['login']
    
    
    if request.method == 'POST':
        req_data = request.form.to_dict()
    else:        
        req_data = request.args.to_dict()
    if 'mod' not in req_data:
        # raise BlinkError(2, 'Input "mod" missing.')
        answer = { 'error': {'text': 'Input "mod" missing.' } }
        return jsonify(answer)  
    
    mod = req_data['mod']
    if not session.get('loggedin',0):
        
        if mod not in allow_without_sess:
            answer = { 'error': {'text':"Session not active."} }
            return jsonify(answer)    
    
    
    page_obj = rest.MainObj()

    
    debug.printx( __name__, 'Session_active?' + str( session.get('loggedin',0) ) )
    answer = page_obj.start(req_data)
  
    return jsonify(answer)   

@app.route('/res/<path:path>')
def send_res(path):
    '''
    send static files: resources of the app
    '''
    stat_tmp = app.static_folder
    return send_from_directory( app.static_folder, path) # static


@app.route('/', methods=['GET', 'POST'])
def start():
    
    req_data = { 'mod':'login' }
    
    mod=None
    
    if request.method == 'POST':
        req_data = request.form.to_dict()
        
        if len(request.files):
            req_data['__FILES__'] = request.files        
        
    else:        
        req_data = request.args.to_dict()

    
    
    if 'mod' in req_data:
        mod = req_data['mod']
        
    if mod==None:
        mod='login'
    

    debug.printx( __name__, 'Session_active?' + str( session.get('loggedin',0) ) )
    #debug.printx( __name__, 'Session-var: (count)' + str( len(session) ) )
    #debug.printx( __name__, 'Session-SID:' + str( session.sid ) )
    # cooksess = request.cookies.get('session')
    # debug.printx( __name__, 'Session-COOKIE:' + str( cooksess ) )

    nowx = time.localtime()
    now_str = "%04u-%02u-%02u %02u:%02u:%02u" % (nowx[0], nowx[1],nowx[2],nowx[3],nowx[4],nowx[5])     
    session['debug_time'] = now_str
    
    forward_cnt = 0
    forward_MAX = 5 # fallback: max 5 forwards ...
    infoarr = {}
    
    while 1:
        page_obj = page_org()
        page_obj.start_page(mod, req_data, config.superglobal)
    
        if page_obj.forward():
            # Internal forwarding ?
            if forward_cnt >= forward_MAX:
                logger.error( 'max forwarding ('+str(forward_MAX)+') reached. Last mod:'+ req_data.get('mod', '') , extra={ 'user': session['sesssec'].get('user',''), 'err_stack':'' } )
                break
            
            req_data = page_obj.forward_get_req()
            mod      = req_data['mod']

            debug.printx(__name__, "INTERN_FORWARD to: "+ str(mod) )
            
            forward_cnt = forward_cnt + 1
            continue # ... repeat the loop ...
            
        break # default break out
        
    if page_obj.page_lib.content_is_file():
        
        file_info = page_obj.page_lib.content_down_file()
        filename  = file_info['filename']
        if not os.path.exists(filename):
            raise BlinkError(1, 'File not found on server.')
        
        debug.printx(__name__, "attachX: "+ str(file_info) )  
        
        return send_file( filename, attachment_filename=file_info['name'], as_attachment=True, cache_timeout=-1 )
        
    else:
        answer = page_obj.get_content()
    
    return answer

@app.template_filter('urlencode')
def urlencode_filter(s):
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return s

# fro DEBUGGING !
if __name__ == "__main__":
    import os
    if 'WINGDB_ACTIVE' in os.environ:
        app.debug = False
    app.run(host='0.0.0.0')