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
    content_length = int(environ.get('CONTENT_LENGTH', None) or '0')
    headers = dict([(k, v) for k, v in environ.items() if k.find("HTTP_") == 0])
    body = None
    if content_length:
        body = environ.get('wsgi.input').read(content_length)
    response_obj = {
        'method': environ.get('REQUEST_METHOD'),
        'path': environ.get('PATH_INFO'),
        'body': body,
        'headers': headers,
        'querystring': environ.get('QUERY_STRING')
    }
    start_response('200 OK', [('Content-type','application/json')])
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
            resp = rest('sample', 'path', 'to', 'resource')
            self.assertTrue(resp.is_json)
            self.assertIsNotNone(resp.json)
            self.assertIsNotNone(resp.json.get('method', None))
            self.assertEqual(resp.json.get('method').lower(), method)

    def test_path(self):
        resp = self.client.get('sample', 'path', 'to', 'resource')
        self.assertTrue(resp.is_json)
        self.assertIsNotNone(resp.json)
        self.assertIsNotNone(resp.json.get('path', None))
        self.assertEqual(resp.json.get('path'), PATH)

    def test_body(self):
        body = "body fixture"
        resp = self.client.post('sample', 'path', 'to', 'resource',
                            data=body, headers={'Content-Length': len(body)})
        self.assertTrue(resp.is_json)
        self.assertIsNotNone(resp.json)
        self.assertIsNotNone(resp.json.get('body', None))
        self.assertEqual(resp.json.get('body'), body)

    def test_query(self):
        resp = self.client.post('sample', 'path', 'to', 'resource',
                                                        query={'foo': 'bar'})
        self.assertTrue(resp.is_json)
        self.assertIsNotNone(resp.json)
        self.assertIsNotNone(resp.json.get('querystring', None))
        self.assertEqual(resp.json.get('querystring'), 'foo=bar')

    def test_headers(self):
        resp = self.client.post('sample', 'path', 'to', 'resource',
                                                        headers={'foo': 'bar'})
        self.assertTrue(resp.is_json)
        self.assertIsNotNone(resp.json)
        headers = resp.json.get('headers', None)
        self.assertIsNotNone(headers)
        self.assertIsNotNone(headers.get('HTTP_FOO', None))
        self.assertEqual(headers.get('HTTP_FOO'), 'bar')

if __name__ == '__main__':
    unittest.main()