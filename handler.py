import sys, os, traceback

try:
    import settings
except ImportError:
    from .utils import create_settings_file
    create_settings_file()
    import settings

try:
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    from http.cookies import SimpleCookie
except ImportError:
    print('Error: localhost only supprts for python3')
    sys.exit(1)

import urllib.parse as urlparse
from urllib.parse import parse_qs

from .response import (
    Response, HttpResponse, render, MEDIA_FILE_FORMAT,
    _error_http404, _error_http500, _render, Http404
)
from .urls import _url_as_list

def _home_page_handler(request):
    with open( os.path.join(request.localserver.LOCALHOST_STATIC_DIR, 'html/ghost-image.html'), 'r') as img:
        ghost_image = img.read()
    return _render(request, 'localhost-home.html', request.localserver.LOCALHOST_TEMPLATE_DIR, context={
        'ghost_image' : ghost_image
    })


def handle(request):  ## for get and post methds

        request.method  = request.command
        request.GET     = dict()
        request.POST    = dict()
        request.COOKIES = SimpleCookie(request.headers.get('Cookie'))

        if request.path[-1]!='/':
            parsed_url  = urlparse.urlparse(request.path+'/')
        else :
            parsed_url  = urlparse.urlparse(request.path)
        query = parse_qs(parsed_url.query)        
        
        for path in Handler.localserver.urlpatterns:
            equal, url_args = path.compare(request,parsed_url.path)
            if equal:
                for key in query:
                    query[key] = query[key][0]
                request.GET = query

                if request.method == 'POST':
                    content_length = int(request.headers['Content-Length']) # <--- Gets the size of data
                    post_data = request.rfile.read(content_length) # <--- Gets the data itself
                    query = parse_qs( post_data.decode('utf-8') )
                    for key in query:
                        query[key] = query[key][0]
                    request.POST = query

                try:
                    resp = path.handler(request, *url_args)
                    if not isinstance(resp, Response):
                        try:
                            raise Exception('return type of function %s is not an instance of Response'%path.handler.__name__)
                        except:
                            resp = _error_http500(request, 'function: "%s"  return type must be an instance of Response'%(path.handler.__name__), traceback.format_exc())
                except Http404:
                    if settings.DEBUG:   resp = render(request, request.localserver.NOTFOUND404_TEMPLATE_PATH, ctx=request.localserver.NOTFOUND404_GET_CONTEXT(request), status_code=404, status_message='NotFound')
                    else:   resp = HttpResponse('<h2>(404) Not Found</h2>', status_code=404, status_message='NotFound')
                except Exception as err:
                    resp = _error_http500(request, str(err), traceback.format_exc())

                ###############################                
                break
        else:
            resp = _error_http404(request)
        
        
        
        request.send_response(resp.status_code, resp.status_message)

        
        ## set cookie, sessionid, csrftoken, ...
        ## test_cookie = SimpleCookie()
        ## test_cookie['test_cookie_3'] = 'this is a test cookie 3'
        #request.send_header('Set-Cookie', test_cookie.output(header='', sep=''))
        for key in resp.headers:
            request.send_header(key, resp.headers[key])
        request.end_headers()
        
        if not resp.is_redirect:
            request.wfile.write(resp.data)

class Handler(SimpleHTTPRequestHandler):
    
    ## static var
    localserver = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        handle(self)
    def do_POST(self):
        handle(self)

    

    def log_message(self, format, *args):
        return
        super().log_message(format, *args)
