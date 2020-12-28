# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""

File:           f_workdir.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
import shutil
from blinkdms.code.lib.debug import debug
from blinkdms.code.lib.main_imports import *

"""
 * sub routines to manage session['globals']["work_path"] / YOUR_SESSION_DIR / SUB_DIRS
 * @example
 
work_lib = f_workdir.main()
work_dir = work_lib.getWorkDir( subDirName )

 """
class main : 

    subDirName=''
    spaceLeftLimit = 500000000 # needed space on work_path in bytes
    initWorkPath=''

    def __init__(self):
        
        initWorkPath = session['globals']["work_path"]
        if (initWorkPath=="") :
            raise BlinkError(1, "Work path is not set. Please contact your administrator.")
        if not os.path.exists(initWorkPath):
            raise BlinkError(2, "Work path not exists. Please contact your administrator.")
        
        self.initWorkPath = initWorkPath
 
    def getSessionMainDir(self) :
        """
        get main session-work dir, no test for existens 
        """    

        session_path = self.initWorkPath + "/pdir_" +  session.sid
        return (session_path)
    
    
    """
     * get work dir
     * @param string subDirName  # name of sub-dir
     * @param string noClean
     * @return path
     """
    def getWorkDir (self,  subDirName,  noClean=0 ) :
        # RETURN: path
    

        if subDirName=="" :
            raise BlinkError(-4, "Need a name for your sub-work-directory")
    
    
        session_path = self.getSessionMainDir()
        #error.set("getWorkDir", -1, "Could not get session-tmp-dir [err:tmperr]:" + tmptext)

    
        try:
            exists = os.path.exists(session_path)
        except:
            exists = 0
            
        if not exists:
            os.makedirs( session_path)
            #     error.set("getWorkDir", -2, "Creating work path 'session_path' failed + "
            #                           . " Please contact your administrator + ")

        self.subDirName=subDirName
    
        subWork_path = session_path + "/" + subDirName
        
        # clean old files NOW ?
        if not noClean:
            self.cleanSubDir()          
    
        if not os.path.exists(subWork_path) :
            try:
                os.makedirs(subWork_path)
            except:
                raise BlinkError(-3,"Creating work path 'subDirName' at 'session_path' failed." + \
                    " Please contact your administrator.") 
    
    
    
        if session['user_glob'].get("g.debugLevel",0) >= 4 :
            debug.printx(__name__, "DEBUG:[4..] getWorkDir():: PATHS: "+session_path+", " + subWork_path)
    
    
        return subWork_path  
     
    
    
    
    """
     *  remove old files and directories in the session-dir
     """
    def cleanSubDir(self) :       
        global error
    
        main_dir = self.getSessionMainDir()

        if ( self.subDirName=="") :
            return (-1)
    
        subWork_path = main_dir + "/" + self.subDirName
        shutil.rmtree(subWork_path, ignore_errors=True) 
        
    
    
    # PUBLIC
    def removeWorkDir(self) :
        global error
    
        main_dir = self.getSessionMainDir() 
        
        if self.subDirName=="":
            return -1
    
    
        # remove files of subDir
        self.cleanSubDir()
    
    
    
    def getAbsDir (self,relpath) : 
        startPath = self.getSessionMainDir()
        abspath = startPath + '/' + relpath
        return abspath
    
    
    """
     * analyse, if enough space is available
     * @param int spaceExpect in bytes
     * @return{'free':, 'expectLeft':)
     """
    def spaceAnalysis(self,spaceExpect) :
    
        total, used, freeSpace = shutil.disk_usage( session['globals']['work_path'] )
        expectSpaceLeft = freeSpace - spaceExpect
        answer = {'free':freeSpace, 'expectLeft': expectSpaceLeft }
    
        if expectSpaceLeft < self.spaceLeftLimit :
            raise BlinkError( 1, 
                'Not enough space left (' + str(expectSpaceLeft) + ') for this amount of data on WORK-dir!' + 
                ' SpaceLeftLimit:' + str(self.spaceLeftLimit) + ' Bytes' )
    
    
        return answer





