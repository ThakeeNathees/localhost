import sys, os
from http.server import HTTPServer

from .handler import (
    Handler, _home_page_handler,
)
from .response import (
    HttpResponse, JsonResponse, Http404,
    render, _get_404_context, redirect, media_response,
    _handle_static_url_localhost, _handle_static_url_developer,
)
from . import auth
from .auth import admin_page
from .urls import Path
from . import utils

__all__ = [
    'Server', 'Path', 'HttpResponse', 'JsonResponse', 'Http404',
    'render', 'redirect', 'media_response',
]

from . import __initialize
__initialize.create_tables()
__initialize.create_dirs()

from server_data import settings
    

class Server:

    def __init__(self, port=8000, server_class=HTTPServer):
        utils._type_check(
            (port, int)
        )

        self.port                   = port
        self.urlpatterns            = []
        
        self.LOCALHOST_STATIC_DIR    = os.path.join(os.path.dirname(__file__), 'static')  ## private static dir,
        self.LOCALHOST_STATIC_URL    = '/_static/'
        self.LOCALHOST_ADMIN_URL     = '/admin/'
        self.LOCALHOST_TEMPLATE_DIR  = os.path.join(self.LOCALHOST_STATIC_DIR, 'html')
        self.LOCALHOST_CTX           = {
            '_static_url'     : self.LOCALHOST_STATIC_URL,
            'static_url'      : settings.STATIC_URL,
            ## in response.py html_base_begin, html_base_end
        }
        self._ERROR_TEMPLATE_PATH          = os.path.join(self.LOCALHOST_STATIC_DIR, 'html/localhost-error.html')
        self.NOTFOUND404_TEMPLATE_PATH     = self._ERROR_TEMPLATE_PATH
        self.NOTFOUND404_GET_CONTEXT       = _get_404_context
        self.BASE_HTML_BEGIN_PATH          = 'localhost-base-begin.html'
        self.BASE_HTML_END_PATH            = 'localhost-base-end.html'

        self._handler_class                 = Handler
        self._handler_class.localserver     = self
        self._server_class                  = server_class 

    def add_default_paths(self): ## urls must ends with /, path is file_path
        if len(self.urlpatterns) == 0 and settings.DEBUG:
            self.urlpatterns.append( Path('', _home_page_handler ) )
        ## TODO: developer has to add admin page    
        self.urlpatterns += [
            Path(settings.STATIC_URL, _handle_static_url_developer),
            Path(self.LOCALHOST_STATIC_URL, _handle_static_url_localhost),
            Path(self.LOCALHOST_ADMIN_URL, admin_page._handle_admin_home_page),
        ]

    def run(self):
        self.add_default_paths()
        server_address = ('', self.port)
        httpd = self._server_class(server_address, self._handler_class)
        print('running server at http://localhost:%s/'%self.port)
        httpd.serve_forever()
