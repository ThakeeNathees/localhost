import sys, os
from http.server import HTTPServer

from .handler import (
    Handler, _handle_static_url_localhost, _handle_static_url_developer
)
from .response import (
    render, HttpResponse, 
    _get_404_context, 
)


class Path:
    def __init__(self, url, handler, name=''):
        if '//' in url :
            raise Exception('Error: %s is not a valid url', url)
        if (url[-1]!='/'):  url +='/'
        if (url[0] != '/'): url = '/'+url
        if not hasattr(handler, '__call__'):
            raise Exception('Error: %s is not callable', handler)

        self.url        = url
        self.handler    = handler
        self.name       = name

    def compare(self, url):
        args = []
        if self.url == url :
            return True, args
        if len(self.url.split('/')) != len(url.split('/')):
            return False, args
        for i in range(1, len(url.split('/')) -1 ): ## '/home/' -> [ '', 'home', '' ]
            if self.url.split('/')[i][0] == '<' and self.url.split('/')[i][-1] == '>':
                args.append(url.split('/')[i])
                continue
            if self.url.split('/')[i] != url.split('/')[i]:
                return False, args
        return True, args

class Server:

    def __init__(self, BASE_DIR, port=8000, server_class=HTTPServer):
        
        self.BASE_DIR               = BASE_DIR
        self.TEMPLATE_DIR           = os.path.join(self.BASE_DIR, 'templates')
        self.STATIC_DIR             = os.path.join(self.BASE_DIR, 'static')
        self.STATIC_URL             = '/static/'

        self.port                   = port
        self.urlpatterns            = []
        
        self.LOCALHOST_STATIC_DIR    = os.path.join(os.path.dirname(__file__), 'static')  ## private static dir,
        self.LOCALHOST_STATIC_URL    = '/_static/'
        self.LOCALHOST_CTX           = {
            '{{ _static_url }}'     : self.LOCALHOST_STATIC_URL,
            '{{ static_url }}'      : self.STATIC_URL,
        }
        self._ERROR_TEMPLATE_PATH          = os.path.join(self.LOCALHOST_STATIC_DIR, 'html/error-base.html')
        self.NOTFOUND404_TEMPLATE_PATH     = self._ERROR_TEMPLATE_PATH
        self.NOTFOUND404_GET_CONTEXT       = _get_404_context
        self.DEBUG                         = True


        self._handler_class                 = Handler
        self._handler_class.localserver     = self
        self._server_class                  = server_class 

    def add_static_paths(self, path, url, func): ## urls must ends with /, path is file_path
        for file in os.listdir(path):
            if not os.path.isdir(os.path.join(path, file)):
                self.urlpatterns.append(
                    Path(url+file, func)
                )
            else:
                self.add_static_paths( os.path.join(path, file) , url+file+'/', func)

    def run(self):
        self.add_static_paths(self.LOCALHOST_STATIC_DIR, self.LOCALHOST_STATIC_URL, _handle_static_url_localhost )
        self.add_static_paths(self.STATIC_DIR, self.STATIC_URL, _handle_static_url_developer)
        for path in self.urlpatterns:
            print(path.url)
        server_address = ('', self.port)
        httpd = self._server_class(server_address, self._handler_class)
        print('running server at http://localhost:%s/'%self.port)
        httpd.serve_forever()


