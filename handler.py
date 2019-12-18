import sys, os, traceback

try:
    from http.server import SimpleHTTPRequestHandler, HTTPServer
except ImportError:
    print('Error: localhost only supprts for python3')
    sys.exit(1)

import urllib.parse as urlparse
from urllib.parse import parse_qs

from .response import Response, HttpResponse, render, IMAGE_FILE_FORMATS

def __static_handler(request, static_dir):
    file_path = os.path.join(static_dir,  '/'.join(request.path.split('/')[2:-1]) ) ## '/static/image.jpg/ -> [ '', static, image.jpg, '' ]
    
    if os.path.exists(file_path) and os.path.isfile(file_path) and file_path.split('.')[-1].lower().replace('/','') in IMAGE_FILE_FORMATS :
        with open(file_path, 'rb') as file:
            content = file.read()
            return Response(status_code=200, status_message='OK', headers = {'Content-type':'image/%s'%file_path.split('.')[-1].lower()}, data=content)
    with open(file_path, 'r') as file:
        if file_path.endswith('.css'):
            return HttpResponse(file.read(), headers={'Content-type':'text/css'})
        elif file_path.endswith('.js'):
            return HttpResponse(file.read(), headers={'Content-type':'text/javascripts'})
        else: raise Exception("InternalError: unknown file type in static : %s"%file_path)

def _handle_static_url_localhost(request):
    return __static_handler(request, request.localserver.LOCALHOST_STATIC_DIR)
def _handle_static_url_developer(request):
    return __static_handler(request, request.localserver.STATIC_DIR)



class Handler(SimpleHTTPRequestHandler):
    
    ## static var
    localserver = None

    def do_GET(self):

        request = self.create_request()
        if self.path[-1]!='/':
            parsed_url  = urlparse.urlparse(self.path+'/')
        else :
            parsed_url  = urlparse.urlparse(self.path)
        query = parse_qs(parsed_url.query)        
        
        for path in Handler.localserver.urlpatterns:
            equal, url_args = path.compare(parsed_url.path)
            if equal:
                for key in query:
                    query[key] = query[key][0]
                request.GET = query

                try:
                    resp = path.handler(request, *url_args)
                except Exception as err:
                    if self.localserver.DEBUG:
                        ## TODO: print stack trace here
                        resp = render(request, self.localserver._ERROR_TEMPLATE_PATH, replace={
                            '{{ title }}':'500 InternalError',
                            '{{ error_message }}' : '(500) InternalError',
                            '{{ error_content }}' : str(err) + '<br>' +traceback.format_exc().replace('\n', '<br>'),
                        }, status_code=500, status_message='InternalError')
                    else:
                        resp = HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
                if not isinstance(resp, Response):
                    if self.localserver.DEBUG:
                        try:
                            raise Exception('return type must be an instance of Response') ## to print stack trace
                        except:
                            resp = render(request, self.localserver._ERROR_TEMPLATE_PATH, replace={
                                '{{ title }}':'500 InternalError',
                                '{{ error_message }}' : '(500) InternalError',
                                '{{ error_content }}' : 'function: "%s"  return type must be an instance of Response<br>%s'%(path.handler.__name__, traceback.format_exc().replace('\n', '<br>'))
                            }, status_code=500, status_message='InternalError')
                    else:
                        resp = HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
                break
        else:
            if self.localserver.DEBUG:
                resp = render(request, self.localserver.NOTFOUND404_TEMPLATE_PATH, replace=self.localserver.NOTFOUND404_GET_CONTEXT(request), status_code=404, status_message='NotFound')
            else:
                resp = HttpResponse('<h2>(404) Not Found</h2>', status_code=404, status_message='NotFound')
        
        self.send_response(resp.status_code, resp.status_message)
        for key in resp.headers:
            self.send_header(key, resp.headers[key])
        self.end_headers()
        self.wfile.write(resp.data)

    def create_request(self, method='GET', GET=dict(), POST=dict()):
        self.method = method
        self.GET    = GET
        self.POST   = POST
        ## TODO: is_user_authenticated, cookies, ...
        return self

    def log_message(self, format, *args):
        super().log_message(format, *args)
