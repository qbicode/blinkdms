'''
error plugin
'''
from blinkdms.code.lib.app_plugin import gPlugin
import sys

class plug_XPL(gPlugin) :  
    '''
     * error plugin
     * @package folder.inc
     * @author  Steffen Kube (steffen@blink-dx.com)
    '''

    def register(self) :

        self.infoarr['title']	= 'Error'
        self.infoarr['layout']	= 'error'


    def startMain(self) :
        pass
        
       