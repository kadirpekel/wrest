import unittest
import time
import json

from multiprocessing import Process
from wsgiref.simple_server import make_server

from wrest import Client

HOST = 'localhost'
PORT = 8000
BASE_URL = "http://%s:%s" % (HOST, PORT)
PATH = '/sample/path/to/resource'

def fixture_app(environ, start_response):
    start_response('200 OK', [('Content-type','application/json')])
    content_length = 0
    try:
        content_length = int(environ.get('CONTENT_LENGTH'))
    except:
        pass
    headers = dict([(k, v) for k, v in environ.items() if k.find("HTTP_") == 0])
    response_obj = {
        'method': environ.get('REQUEST_METHOD'),
        'path': environ.get('PATH_INFO'),
        'body': environ.get('wsgi.input').read(content_length),
        'headers': headers,
        'querystring': environ.get('QUERY_STRING')
    }
    return json.dumps(response_obj)

class TestCaseWrest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = make_server(HOST, PORT, fixture_app)
        cls.server_proc = Process(target=cls.server.serve_forever)
        cls.server_proc.start()
        time.sleep(1) # Let server start in parallel execution
        cls.client = Client(BASE_URL)

    @classmethod
    def tearDownClass(cls):
        cls.server_proc.terminate()

    def test_methods(self):
        for method in ['get', 'post', 'put', 'delete']:
            rest = getattr(self.client, method)
            resp, info = rest('sample', 'path', 'to', 'resource')
            self.assertEqual(resp['method'].lower(), method)

    def test_path(self):
        resp, info = self.client.get('sample', 'path', 'to', 'resource')
        self.assertEqual(resp.get('path'), PATH)

if __name__ == '__main__':
    unittest.main()