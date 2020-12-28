# REST calls

#import requests
import json
from requests import Request, Session
import hashlib
import base64

from blinkdms.conf import conf_unittest
from test._test_subs import utilities

class Rest_help:
    '''
    
    :example:
    
    rest_lib = rest.Rest_help()
    jsonrpc_lib.crea_empty_session()
    argu={}
    user='test'
    jsonrpc_lib.login(argu, user)
    # --- or
    device='BOX2'
    jsonrpc_lib.login_dev(argu, device)
    '''
    
    cooki_x=None
    
    def __init__(self):

        self.post_url   = conf_unittest.ut_conf['test.url'] + '/api/rest'
        self.ssl_verify = conf_unittest.ut_conf['test.ssl_verify']
        
        utilities.print_debug('REST_URL:'+self.post_url)
    
    def crea_empty_session(self):
        self.sess_obj = Session()
        self.cooki_x  = None
        
    def get_full_url(self, method, argu):
        post_url = self.post_url + '?mod='+method
        for key,val in argu.items():
            post_url = post_url + '&'+key+'='+str(val)
            
        return post_url
    
    def send_it(self,  method, argu ):
        '''
        :return : {'data': ...}
        '''
        
        get_url = self.get_full_url(method, argu)
         
        req = Request('GET', get_url, cookies = self.cooki_x)
        prepped = req.prepare()
        resp = self.sess_obj.send(prepped, verify=self.ssl_verify)
        #print ("RESP:" + resp.text)  
        
        cooki_x = self.sess_obj.cookies
        #print ("COOK: " + str(cooki_x) )   
        
        res_dict = json.loads(resp.text)
        return res_dict
    
    def send_crea_cookie(self,  method, argu ):
        '''
        sub method
        '''
        
        auth_headers = {'Content-Type': 'application/json'}

        get_url = self.get_full_url(method, argu)
        
        self.sess_obj = Session()
        req = Request('GET', get_url, headers=auth_headers)
        prepped = req.prepare()
        resp = self.sess_obj.send(prepped, verify=self.ssl_verify)
        self.cooki_x = self.sess_obj.cookies
        
        
        res_dict = json.loads(resp.text)
        return res_dict
    
    def login(self, argu, username, pw='' ):
        '''
        normal user login, take password from config
        '''

        argu['go']   = 1
        argu['user'] = username
        argu['password'] = pw   
        
        utilities.print_debug('Login (user): User:'+username )
        answer = self.send_crea_cookie('login', argu)   
        
        if 'error' in answer:
            raise ValueError('Login error: '+ str(answer['error'] ) )
        
        if 'data' not in answer:
            raise ValueError('General JSONRPC error' )        
        
       
        
        return answer
    
    def logout(self):
        argu={}
        self.send_it('logout', argu )
    