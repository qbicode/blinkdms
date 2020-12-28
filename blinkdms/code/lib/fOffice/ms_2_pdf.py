# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
produce PDF document from microsoft word
File:           ms_2_pdf.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""
import os
import sys
import subprocess
import re
import shutil
import logging

from flask import session
from blinkdms.code.lib.debug import debug

logger = logging.getLogger()

class LibreOfficeError(Exception):
    
    def __str__(self):
        return self.errtext    
    
    def __init__(self, output):
        self.errtext = output 
        print ('(23) ERROR:' +output)

class MS_2_pdf:
    
    def __init__(self):
        pass
        
    def convert_to_pdf(self, source, outfile, timeout=None):
        
        ext_pos     = source.rfind('.')
        if ext_pos<0:
            ext_pos = len(ext_pos)
        source_base = source[0:ext_pos] 
        
        dir_pos    = source.rfind('/')
        source_dir = source[0:dir_pos]    
        
        my_env = os.environ.copy()
        debug.printx(__name__, "(47): ENV: "+ str(my_env) )
        #my_env["HOME"] = "/tmp/blinkdms_home"       
        
        args = [ '/usr/bin/lowriter', '--convert-to', 'pdf', '--outdir', source_dir, source]
        
        if not os.path.exists(source):
            raise LibreOfficeError('Input file "'+source+'" not found.')        
    
        process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,  env=my_env )

        
        filename_tmp_out = source_base+'.pdf'
        proc_output = process.stdout.decode()
        proc_strerr = process.stderr.decode()
        
        # logger.error( '(53) pdf_convert source: '+source, extra={ 'user': session['sesssec'].get('user',''), 'err_stack':None } ) 
        
        if not os.path.exists(filename_tmp_out):
            debug.printx(__name__, "(58): Source: "+source+ ' SYSCMD:'+ str(args) + ' STERR: '+str(proc_strerr))
            raise LibreOfficeError('Output file "'+filename_tmp_out+'" not found. Info: '+proc_output )
        
        if not os.path.getsize(filename_tmp_out):
            raise LibreOfficeError('PDf file is empty.')
 
        shutil.copyfile(filename_tmp_out, outfile)

    
if __name__ == "__main__":
    
    # data_path = r'C:\Users\Steffen\Documents\Code\blinkdms\test\blinkdms'
    data_path = '/opt/blinkdms/test/blinkdms'
    filename_ori= os.path.join(data_path, 'code/lib/oVERSION/Vorlage_SOP_t1.030.1')
    filename_new= os.path.join(data_path, 'code/lib/oVERSION/Vorlage_SOP_x1.tr2.pdf')

    print ('CONVERT: '+ filename_ori)

    a = MS_2_pdf()
    a.convert_to_pdf(filename_ori, filename_new)
    
    
    print('READY')