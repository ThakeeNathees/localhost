import sys, os
from http.server import HTTPServer

from .handler import (
    Handler, _home_page_handler,
)
from .response import (
    HttpResponse, JsonResponse, Http404,
    render, _get_404_context, redirect, media_response,
    _static_handler
)
from . import auth
from .auth import admin_page
from .urls import Path
from . import utils

try:
    from server_data import settings
except ImportError:
    raise Exception('did you initialize with "python localhost init [path]" ?')
    

class Server:

    def __init__(self, port=8000, server_class=HTTPServer):
        utils._type_check(
            (port, int)
        )

        self.port                   = port
        self.urlpatterns            = []

        self._handler_class                 = Handler
        self._handler_class.localserver     = self
        self._server_class                  = server_class 

    def add_default_paths(self): ## urls must ends with /, path is file_path
        if len(self.urlpatterns) == 0 and settings.DEBUG:
            self.urlpatterns.append( Path('', _home_page_handler ) )
        
        self.urlpatterns += [
            Path(settings.STATIC_URL, _static_handler),
        ]
        ## admin pages
        USE_ADMIN_PAGE = settings.__dict__['USE_ADMIN_PAGE'] if hasattr(settings, 'USE_ADMIN_PAGE') else True 
        if USE_ADMIN_PAGE:
            ADMIN_URL = settings.__dict__['ADMIN_ULR'] if hasattr(settings, 'ADMIN_URL') else '/admin/'

            self.urlpatterns += [
                Path(ADMIN_URL, admin_page._handle_admin_home_page, name='admin-home'),
                Path(ADMIN_URL+'login/', admin_page._handle_admin_login_page, name='admin-login'),
                Path(ADMIN_URL+'logout/', admin_page._handle_admin_logout_page, name='admin-logout'),
                Path(ADMIN_URL+'<app_name>/<table_name>', admin_page._handle_admin_table_page),
            ]
                


    def run(self):
        self.add_default_paths()
        server_address = ('', self.port)
        httpd = self._server_class(server_address, self._handler_class)
        print('running server at http://localhost:%s/'%self.port)
        httpd.serve_forever()
