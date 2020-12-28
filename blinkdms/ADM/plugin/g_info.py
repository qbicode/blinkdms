'''
Admin info plugin
'''

from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin


class plug_XPL(gPlugin) :  
    '''
    
     * @package g_settings.py
     * @author  Steffen Kube (steffen@blink-dx.com)
    :params: 
      "action" :  
         'session_vars' 
         'db_cache'
         
    '''

    def register(self) :
        self.infoarr['title']	= 'General Info views'
       
        self.infoarr['layout']	= 'ADM/g_info'        
        self.infoarr['locrow']  = [ {'url':'ADM/home', 'text':'Home'} ]
    
    def _build_table(self, table_key, title, data):
        '''
        build one table
        
        '''
        data_rows=[]
        one_table =  {
          'header': {
             'title' : title,
          },
         'cols' : [],  # OPTIONAL
         'data' : data_rows,   # list of rows                
        }   
        
        for key, val in data.items():
            data_rows.append( [key, str(val)] )
            
        self.massdata['t'].append(one_table)
        
    def _build_table_globals(self):
        '''
        build one table GLOBALS
        '''
        
        key = 'globals'
        data_cpy = session[key].copy()
       
        if 'db' in data_cpy:
            for dbid, db_info in data_cpy['db'].items():
                data_cpy['db'][dbid]['password'] = '***'        
        
        data_rows=[]
        one_table =  {
          'header': {
             'title' : key,
          },
         'cols' : ['KEY', 'VAL', 'SUBVAL'],  # OPTIONAL
         'data' : data_rows,   # list of rows                
        }   
        
        for key, val in data_cpy.items():
            if key=='db':
                for db_id, db_info in val.items():
                    data_rows.append( [key+':'+ db_id , str(db_info)] )
            else:
                data_rows.append( [key, str(val)] )
            
        self.massdata['t'].append(one_table)    
    
    def act_session_vars(self, db_obj):
        
        self.massdata['t'] = []
        
        
        self._build_table_globals()    
        
        key = 'user_glob'
        self._build_table(key, key, session[key])
        
        key = 'sessvars'
        self._build_table(key, key, session[key]) 
        
        key = 'sesssec'
        data_cpy = session['sesssec'].copy()
        data_cpy['password'] = '***' 
        if 'dbacc' in data_cpy:
            if  'password' in data_cpy['dbacc']:
                data_cpy['dbacc']['password']='***'
            
        self._build_table(key, key, data_cpy)

    def act_db_cache(self, db_obj):
        
        self.massdata['t'] = []
        
        data_rows=[]
        one_table =  {
          'header': {
             'title' : 'Main tables',
          },
         'cols' : [],  # OPTIONAL
         'data' : data_rows,   # list of rows                
        }   
        for table, dummy in session['db_cache']['tables'].items():
            data_rows.append( [table] )   
        self.massdata['t'].append(one_table) 
        
        data_rows2=[]
        one_table2 =  {
          'header': {
             'title' : 'Columns',
          },
         'cols' : [],  # OPTIONAL
         'data' : data_rows2,   # list of rows                
        }   
        for table, tab_data in session['db_cache']['tables'].items():
            cols = tab_data.get('cols', {} )
            for col, col_feat in cols.items():
                data_rows.append( [table, col, str(col_feat)] ) 
            
        self.massdata['t'].append(one_table2)                 

    def startMain(self) :
        
        self.massdata = {}
        
        db_obj = self._db_obj1
        
        action =  self._req_data.get('action', '')
        self._html.add_meta('action', action)
        
        if action=='':
            raise BlinkError(1,'No action given.')
       
        self._html.add_meta( 'action' , action)    
        if action=='session_vars':
            self.act_session_vars(db_obj)
        if action=='db_cache':
            self.act_db_cache(db_obj)        

        
    def mainframe(self):
        self.sh_main_layout(massdata = self.massdata )    
