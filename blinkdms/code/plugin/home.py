'''
home plugin
'''
from blinkdms.code.lib.main_imports import *
from blinkdms.code.lib.app_plugin import gPlugin
from blinkdms.code.plugin.subs import obj_list_show
from blinkdms.code.lib import oROLE

class plug_XPL(gPlugin) :  
    '''
     * home plugin
     * @package folder.inc
     * @author  Steffen Kube (steffen@blink-dx.com)
    '''

    def register(self):
        
        context = session['sesssec']['my.context']
        if context=='EDIT':
            layout='home_edit'
        else:
            layout='home_active'

        self.infoarr['title']  = 'Home'
        self.infoarr['layout'] = layout
        
        if  context=='EDIT':
            self.infoarr['role.need'] = [oROLE.ROLE_KEY_EDIT]


    def startMain(self) :
        # get device num and so on
        
        db_obj = self._db_obj1
        db_obj2 = self.db_obj2()
        self.massdata = {}
        list_lib = obj_list_show.ShowList(self.massdata, self._req_data)
        list_lib.start(db_obj, db_obj2)
        
    def mainframe(self):
        self.sh_main_layout(massdata=self.massdata)


