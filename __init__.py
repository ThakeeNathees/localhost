import sys, os

from .handler import Handler, HttpResponse, render
from http.server import HTTPServer



        


class Path:
    def __init__(self, url, handler, name=''):
        if (url[-1]!='/'):  url +='/'
        if (url[0] != '/'): url = '/'+url
        if not hasattr(handler, '__call__'):
            raise Exception('Error: %s is not callable', handler)

        self.url        = url
        self.handler    = handler
        self.name       = name

    def is_equal(self, url):
        ##TODO: self.path is a pattern, path is string compare
        return self.url == url    

class Server:

    def __init__(self, BASE_DIR, port=8000, server_class=HTTPServer):
        
        self.BASE_DIR               = BASE_DIR
        self.TEMPLATE_DIR           = os.path.join(self.BASE_DIR, 'templates')
        self.STATIC_DIR             = os.path.join(self.BASE_DIR, 'static')
        self.DEBUG                  = True

        self.port                   = port
        self.urlpatterns            = []
        self.template_path          = ''
        
        self._handler_class                 = Handler
        self._handler_class.localserver     = self
        self._server_class                  = server_class 
    
    def run(self):
        server_address = ('', self.port)
        httpd = self._server_class(server_address, self._handler_class)
        print('running server at http://localhost:%s/'%self.port)
        httpd.serve_forever()