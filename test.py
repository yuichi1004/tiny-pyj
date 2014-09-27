import BaseHTTPServer
import tinypyj
import json
import threading
import time
import urlparse
import unittest
import base64
import sys

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def handle_method(self, method, args):
        if method == 'getStr':
            return {'result': 'test result'}
        elif method == 'add':
            r = int(args['a']) + int(args['b'])
            if 'c' in args:
                r += int(args['c'])
            return {'result': r}
        elif method == 'sub':
            r = int(args['a'])  - int(args['b'])
            return {'result': r}
        elif method == 'raiseError':
            return {
                'error': {
                    'code': -32603,
                    'message': 'Internal Error'
                }
            }
        return None

    def do_POST(self):
        self.send_response(200)
        self.send_header('ContentType', 'application/json')
        self.end_headers()
        clen = int(self.headers['content-length'])
        reqbody = self.rfile.read(clen)
        reqjson = json.loads(reqbody)

        x = {'jsonrpc':'2.0', 'id': reqjson['id']}
        y = self.handle_method(reqjson['method'], reqjson['params'])
        respjson = dict(list(x.items()) + list(y.items()))

        self.wfile.write(json.dumps(respjson))

    def do_GET(self):
        self.send_response(200)
        self.send_header('ContentType', 'application/json')
        self.end_headers()
        
        query = urlparse.urlparse(self.path).query
        query_params = urlparse.parse_qs(query)
        params ={}
        if 'params' in query_params:
            params = json.loads(base64.b64decode(query_params['params'][0]))
        
        x = {'jsonrpc':'2.0', 'id': query_params['id'][0]}
        y = self.handle_method(query_params['method'][0], params)
        respjson = dict(list(x.items()) + list(y.items()))

        self.wfile.write(json.dumps(respjson))

    def log_message(self, *args):
        pass
        

class TestServerThread(threading.Thread):
    def __init__(self):
        super(TestServerThread, self).__init__()
    def run(self):
        httpd = BaseHTTPServer.HTTPServer(('', 8000), MyHandler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()

class TinyPyjTest(unittest.TestCase):
    def setUp(self):
        smd = json.loads(open('./smds/test.smd.json').read())
        self.c = tinypyj.Client(smd, 'http://localhost:8000')
    
    def test_call(self):
        resp = self.c.get_str()
        self.assertEqual('test result', resp)

    def test_with_params(self):
        resp = self.c.add(3, 4, 5)
        self.assertEqual(12, resp)
    
    def test_without_optional_params(self):
        resp = self.c.add(3, 4)
        self.assertEqual(7, resp)
    
    def test_with_params_get(self):
        resp = self.c.sub(5, 2)
        self.assertEqual(3, resp)
    
    def test_error(self):
        self.assertRaises(tinypyj.RpcError, self.c.raise_error)
        

if __name__ == '__main__':
    t = TestServerThread()
    t.daemon = True
    t.start()
    
    unittest.main()

