import sys, os
try:
    from http.server import SimpleHTTPRequestHandler, HTTPServer
except ImportError:
    print('Error: localhost only supprts for python3')
    sys.exit(1)

import urllib.parse as urlparse
from urllib.parse import parse_qs

from.response import Response, HttpResponse, render

def _get_404_context(request):
    ctx = dict()
    ctx['{{ error_message }}'] = '(404) Page Not Found'
    ctx['{{ title }}'] = '404 NotFound'
    paths = ''
    for path in request.localserver.urlpatterns:
        paths += '<li>'+ path.url+'</li>'
    ctx['{{ error_content }}'] = '<p>supported url patterns:<ol>%s<ol></p>'%paths 
    return ctx

class Handler(SimpleHTTPRequestHandler):
    
    ## static var
    localserver = None

    def do_GET(self):

        if (self.path[-1]!='/'): self.path+='/'
        request = self.create_request()
        
        for path in Handler.localserver.urlpatterns:
            if path.is_equal(self.path):
                parsed_url  = urlparse.urlparse(self.path)
                query       = parse_qs(parsed_url.query)
                url_args    = [] ## TODO: create with urlpatterns
                for key in query:
                    query[key] = query[key][0]
                request.GET = query

                resp = path.handler(request, *url_args)
                if not isinstance(resp, Response):
                    if self.localserver.DEBUG:
                        ## TODO: print stack trace here
                        resp = HttpResponse('<h2 style="color:red">(500) InternalError: handler return type must be an instance of Response</h2>', status_code=500, status_message='InternalError')
                    else:
                        resp = HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
                break
        else: ## TODO:not found
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

'''
def load_image(file):
    with open(file, 'rb') as file:
        return file.read()

def image_request(request):
    print(request.path)
    request.send_response(200, 'OK')
    request.send_header('Content-type', 'image/jpeg')
    request.end_headers()
    ##request.wfile.write(bytes('hello from server', 'UTF-8'))
    request.wfile.write(load('./localhost/index.jpeg'))
    pass

'''