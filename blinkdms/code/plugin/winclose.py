'''
close window
'''
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
import sys

class plug_XPL(gPlugin) :  
    '''
     * close window plugin
     * @package winclose.py
     * @author  Steffen Kube (steffen@blink-dx.com)
     :param t: tablename
    '''

    def register(self) :

        self.infoarr['title']	= 'Close'
        self.infoarr['layout']	= 'winclose'


    def startMain(self) :
        
        table = self._req_data['t']
        
        if len( session['sessvars'].get('formback',{}) ):
            if len( session['sessvars']['formback'].get(table,{}) ):
                session['sessvars']['formback'].pop(table, None)

        self.sh_main_layout()