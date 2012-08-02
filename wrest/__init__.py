import urllib2, base64, json

class RestRequest(urllib2.Request):
    """Since urllib2 `Request` class supports only the http methods of 'GET'
    and 'POST', this subclass is intended to support all of them.
    """

    def __init__(self, url, method, **kwargs):
        """Overrides `urllib2.Request` class constructor to provide `method`
        keyword arg in addition to other super keyword args.

        Arguments:
        url -- actual url which http request is gonna be sent
        method -- name of one of http methods

        Keyword Arguments:
        **kwargs -- `urllib2.Request` class constructor's keyword args
        """
        urllib2.Request.__init__(self, url, **kwargs)
        self.method = method

    def get_method(self):
        """Overrides `urllib2.Request.get_method` to able to return varity of
        http methods.
        """
        return self.method or urllib2.Request.get_method(self)

class Client(object):
    """ Actual class does the rest operations."""

    HTTP_METHODS = ('get', 'head', 'post', 'put', 'delete')

    def __init__(self, base_url):
        """ Constructor

        Arguments:
        base_url -- the url identifies the root path of rest service
        """
        self.base_url = base_url

        # Dynamically bind http verbs as instance functions
        def bind_method (method):
            def f(*args, **kwargs):
                return self.rest(method, *args, **kwargs)
            return f
        for method in Client.HTTP_METHODS:
            setattr(self, method, bind_method(method))

    def request(self, path, method="GET", headers={}):
        """ Make http request in order to retrieve a valid http response.

        Arguments:
        path -- path of resource relative to base url

        Keyword Arguments:
        method -- name of one of http methods
        headers -- dictionary object which represents http headers
        """
        url = "%s%s" % (self.base_url, path or '')
        req = RestRequest(url, method=method or 'GET')
        for k, v in headers.items() or {}: req.add_header(k, v)
        resp = urllib2.urlopen(req)
        body = resp.read()
        resp.close()
        info = dict(resp.info())
        content_type = info.get('content-type', None)
        if content_type and content_type.lower().find('application/json') >= 0:
            return json.loads(body)
        return body

    def rest(self, method, *args, **kwargs):
        """ Simplifies http requests by mapping *args to path and **kwargs to
        querystring components.

        Arguments:
        method -- name of one of http methods
        *args -- list of path components
        **kwargs -- dict of querystring components
        """
        headers = kwargs.pop('headers', {})
        qs = "&".join(["=".join((str(k), str(v))) for k, v in kwargs.items()])
        path = "/%s?%s" % ("/".join(args), qs)
        return self.request(path, method, headers)
