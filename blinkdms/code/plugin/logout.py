"""
manage logout

File:           logout.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
from flask import session

from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib import oUSER_PREF



class plug_XPL(gPlugin) :  
    '''
     * home plugin
     * @package folder.inc
     * @author  Steffen Kube (steffen@blink-dx.com)
    '''

    def register(self) :

        self.infoarr['title']	= 'Logout'
        self.infoarr['layout']	= 'logout'


    def startMain(self) :
        
        if 'sesssec' in session:
            try:

                # just save prefs, if session is still active
                db_obj = self.db_obj2()
                oUSER_PREF.MainLib.save(db_obj)
                
            except:
                pass # do not handle this 

        session['loggedin'] = 0    # deactivate session
        session['sesssec']  = {}
        
    def mainframe(self):
        self.sh_main_layout()
        
   
           