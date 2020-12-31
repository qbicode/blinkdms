#
import requests
import json
from requests import Request, Session
import hashlib
import base64
from requests import Request, Session

from blinkdms.conf import conf_unittest
from test._test_subs import utilities

class Jsonrpc_help:
    '''
    
    :example:
    
    jsonrpc_lib = jsonrpc.Jsonrpc_help('hube')
    jsonrpc_lib.crea_empty_session()
    argu={}
    user='test'
    jsonrpc_lib.login(argu, user)
    # --- or
    device='BOX2'
    jsonrpc_lib.login_dev(argu, device)
    '''
    
    cooki_x=None
    
    def __init__(self, app_type):

        self.post_url   = conf_unittest.ut_conf['test.url'][app_type] + '/api/json'
        self.ssl_verify = conf_unittest.ut_conf['test.ssl_verify']
        
        utilities.print_debug('JSONRPC_URL:'+self.post_url)
    
    def crea_empty_session(self):
        self.sess_obj = Session()
        self.cooki_x  = None
    
    def send_it(self,  method, argu ):
        '''
        :return : {'data': ...}
        '''
        
        get_info_payload = {"jsonrpc": "2.0", "params":  [argu,], "id": "3", "method": method}    
        req = Request('POST', self.post_url, json=get_info_payload, cookies = self.cooki_x)
        prepped = req.prepare()
        resp = self.sess_obj.send(prepped, verify=self.ssl_verify)
        #print ("RESP:" + resp.text)  
        
        cooki_x = self.sess_obj.cookies
        #print ("COOK: " + str(cooki_x) )   
        
        res_dict = json.loads(resp.text)
        return res_dict
    
    def send_crea_cookie(self,  method, argu, userpass ):
        '''
        sub method
        '''
        rpc_auth = "Basic %s" % base64.b64encode(userpass.encode("ascii")).decode("utf-8")
        auth_headers = {'Content-Type': 'application/json', 'Authorization': rpc_auth}
        
        get_info_payload = {"jsonrpc": "2.0", "params": [argu,] , "id": "2", "method": method}
        
        self.sess_obj = Session()
        req = Request('POST', self.post_url, json=get_info_payload, headers=auth_headers)
        prepped = req.prepare()
        resp = self.sess_obj.send(prepped, verify=self.ssl_verify)
        self.cooki_x = self.sess_obj.cookies
        #print ("RESP: " + resp.text) 
        #print ("COOK: " + str(self.cooki_x) )   
        
        res_dict = json.loads(resp.text)
        return res_dict
    
    def login(self, argu, user_key, pw='' ):
        '''
        normal user login, take password from config
        '''
        
        username = conf_unittest.ut_conf['users'][user_key]['user']
        if pw=='':
            pw = conf_unittest.ut_conf['users'][username]['pw']
        
        userpass = username +":"+ pw
        utilities.print_debug('Login (user): User:'+username )
        answer = self.send_crea_cookie('login', argu, userpass)   
        
        if 'result' not in answer:
            raise ValueError('General JSONRPC error' )        
        
        if 'error' in answer['result']:
            raise ValueError('Login error: '+ str(answer['result']['error'] ) )
        
        return answer
    
    def logout(self):
        argu={}
        self.send_it('logout', argu )
    
   