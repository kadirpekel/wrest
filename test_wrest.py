import unittest
from multiprocessing import Process
from bottle import route, run, request
from wrest import Client
import time

HOST = 'localhost'
PORT = 8000
BASE_URL = "http://%s:%s" % (HOST, PORT)
PATH = '/sample/path/to/resource'

@route(PATH, method=['GET', 'POST', 'PUT', 'DELETE'])
def echo():
    return {
        'method': request.method,
        'path': request.path,
        'body': request.body.read(),
        'headers': dict(request.headers),
        'querystring': dict(request.query)
    }

class TestCaseWrest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = Process(target=run, kwargs={'host': HOST, 'port': PORT})
        cls.server.start()
        time.sleep(1) # Let server start in parallel execution
        cls.client = Client(BASE_URL)
    
    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()

    def test_methods(self):
        for method in ['get', 'post', 'put', 'delete']:
            rest = getattr(self.client, method)
            resp = rest('sample', 'path', 'to', 'resource')
            self.assertEqual(resp['method'].lower(), method)

    def test_path(self):
        resp = self.client.get('sample', 'path', 'to', 'resource')
        self.assertEqual(resp.get('path'), PATH)

if __name__ == '__main__':
    unittest.main()