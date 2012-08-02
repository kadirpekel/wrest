import urllib2, base64, json

class RestRequest(urllib2.Request):

    def __init__(self, url, **kwargs):
        self.method = kwargs.pop('method', None)
        urllib2.Request.__init__(self, url, **kwargs)

    def get_method(self):
        return self.method or urllib2.Request.get_method(self)

class Client(object):

    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url
        self.credentials = username and password and (username, password) or None

    def request(self, path, method):
        url = "%s%s" % (self.base_url, path or '')
        req = RestRequest(url, method=method or 'GET')
        if self.credentials:
            base64string = base64.encodestring('%s:%s' % self.credentials)
            req.add_header("Authorization", "Basic %s" % base64string)
        resp = urllib2.urlopen(req)
        body = resp.read()
        resp.close()
        info = dict(resp.info())
        content_type = info.get('content-type', None)
        if content_type and content_type.lower().find('application/json') >= 0:
            return json.loads(body)
        return body

    def rest(self, *args, **kwargs):
        method = kwargs.pop('method', 'GET')
        url = "/%s?%s" % ("/".join(args), "&".join(["=".join((str(k), str(v))) for k, v in kwargs.items()]))
        return self.request(url, method=method)
