import urllib2, json, base64

class ClientRequest(urllib2.Request):
    """Since urllib2 `Request` class supports only the http methods of 'GET'
    and 'POST', this subclass is intended to support all of them.
    """

    def __init__(self, url, method, **kwargs):
        """Overrides `urllib2.Request` class constructor to provide `method`
        keyword arg in addition to other super keyword args.

        Arguments:
        url -- actual url which http request is gonna be sent
        method -- name of one of http methods, must be uppercased.

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

    HTTP_METHODS = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE')

    def __init__(self, base_url, request_class=ClientRequest, username=None,
                                                    password=None, debug=False):
        """ Constructor

        Arguments:
        base_url -- the url identifies the root path of rest service
        request_class -- class ref to instantiate as internal request instances
        username -- username to use for basic authentication
        password -- password to use for basic authentication
        debug -- flag if want to print out some debugging information
        """
        self.base_url = base_url
        self.request_class = request_class
        self.username = username
        self.password = password
        self.debug = debug
        
        # Dynamically bind http verbs as instance functions
        def bind_method (method):
            def f(*args, **kwargs):
                kwargs['method'] = method
                return self.rest(*args, **kwargs)
            return f
        for method in Client.HTTP_METHODS:
            setattr(self, method.lower(), bind_method(method))

    def request(self, method, path, query=None, data=None, headers=None):
        """ Make http request in order to retrieve a valid http response.

        Arguments:
        method -- name of one of http methods
        path -- path of resource relative to base url
        query -- query string dictionary
        data -- request body
        headers -- dictionary object which represents http headers
        """

        qs = ''
        if query:
            qs = "?" + "&".join(["=".join((k, v)) for k, v in query.items()])
        url = "%s%s%s" % (self.base_url, path or '/', qs)
        if self.debug:
            print("%s %s" % (method, url))
        req = self.request_class(url, method=method.upper() or 'GET')
        if self.username and self.password:
            base64string = base64.encodestring(
                                    '%s:%s' % (self.username, self.password))
            req.add_header("Authorization", "Basic %s" % base64string) 
        if headers:
            for k, v in headers.items(): req.add_header(k, v)
        resp = urllib2.urlopen(req, data)
        body = resp.read()
        resp.close()
        info = resp.info()
        content_type = info.get('content-type', None)
        if content_type and content_type.lower().find('application/json') >= 0:
            return (json.loads(body), info)
        return (body, info)

    def rest(self, *args, **kwargs):
        """ Simplifies http requests by mapping *args to path and **kwargs to
        other request components.

        Arguments:
        *args -- list of path components

        Keyword Arguments:
        method -- name of one of http methods
        query -- query string dictionary
        headers -- dictionary object which represents http headers
        data -- request body
        """
        method = kwargs.pop('method', None)
        path = "/%s" % "/".join(args)
        return self.request(method, path, **kwargs)
