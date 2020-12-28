# simple Flask Mock Server
# https://gist.github.com/eruvanos/f6f62edb368a20aaa880e12976620db8

import requests
import uuid

from flask import Flask, jsonify
from threading import Thread

import unittest
import requests


class MockServer(Thread):
    def __init__(self, port=5000):
        super().__init__()
        self.port = port
        self.app = Flask(__name__)
        self.url = "http://localhost:%s" % self.port

        self.app.secret_key = 'ieiw828xycx' # secret key for SESSION
        self.app.add_url_rule("/shutdown", view_func=self._shutdown_server)

    def _shutdown_server(self):
        from flask import request
        if not 'werkzeug.server.shutdown' in request.environ:
            raise RuntimeError('Not running the development server')
        request.environ['werkzeug.server.shutdown']()
        return 'Server shutting down...'

    def shutdown_server(self):
        requests.get("http://localhost:%s/shutdown" % self.port)
        self.join()

    def add_callback_response(self, url, callback, methods=('GET',)):
        callback.__name__ = str(uuid.uuid4())  # change name of method to mitigate flask exception
        self.app.add_url_rule(url, view_func=callback, methods=methods)

    def add_json_response(self, url, serializable, methods=('GET',)):
        def callback():
            return jsonify(serializable)
        
        self.add_callback_response(url, callback, methods=methods)

    def run(self):
        self.app.run(port=self.port)
        

class BlinkTestCls(unittest.TestCase):
    
    url=''
    
    def setUp(self):
        self.server = MockServer()
        self.server.start()
        
    def add_file_as_url(self, filename, methodname):
        # file name => URL
        SEP='/'
        START_PAT='blinkdms'
        if filename.find(SEP) <0:
            SEP='\\'
            
        start_pos = filename.find(SEP + START_PAT + SEP) 
        use_path  = filename[start_pos:]
        url = "/" + use_path.replace(SEP, '_')
        url = url.replace('.py', '')
        self.url = url # store url
        self.server.add_callback_response(url, methodname)
        
        return url
    
    def request_get(self, url):
        response  = requests.get(self.server.url + url)
        return response

    def tearDown(self):
        self.server.shutdown_server()