# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

"""
config file for BlinkDMS
set superglobal
File:           config.py
Copyright:      Blink AG   
Author:         Steffen Kube <steffen@blink-dx.com>
"""


superglobal = {}
superglobal['site.title']     ='Blink DMS'
superglobal['system.company'] ='Blink AG'
superglobal['company.url']    ='https://www.blink-dx.com'
superglobal['admin.email']    ='root@xxxx.com'
superglobal['gui.root_dir']   ='.'  # starting from ROOT DIR, contains res, templates



superglobal['ldap'] = {
    'ldap_server': 'ldap://jenblidc01.blink.lan',
    'user_domain': 'blink.lan'
}

superglobal['db'] = {

   'main':  {
       'dbname':'dmsdb',
       'host':'localhost',
       'user':'blinkdms',
       'password':'XXX',
     }   
    }
superglobal['db.std_config_id'] = 'main' # standard index for superglobal['db']

superglobal['work_path']   = "/data/blinkdms/work"
superglobal['data_path']   = "/data/blinkdms/docs"

# 'ANY': anybody is allowed or 'qm': only qm is allowed to release
superglobal['app.version.release.role']    = 'ANY' 
superglobal['workflow.sign.password.need'] = 0 # user must give a password on workflow signing ? 0 or 1

superglobal['email.send.allow'] = 1 # 0 or 1 
