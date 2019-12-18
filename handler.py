import sys, os
try:
    from http.server import SimpleHTTPRequestHandler, HTTPServer
except ImportError:
    print('Error: localhost only supprts for python3')
    sys.exit(1)

import urllib.parse as urlparse
from urllib.parse import parse_qs



class Response:
    def __init__(self, status_code=200, status_message='OK', headers = {'Content-type':'text/html'}, data=bytes('','UTF-8')):
        self.status_code        = status_code
        self.status_message     = status_message
        self.headers            = headers
        self.data               = data


class HttpResponse(Response):
    def __init__(self, response_string, status_code=200, status_message='OK', headers = {'Content-type':'text/html'}):
        super().__init__(status_code=status_code, status_message=status_message, headers = headers, data=bytes(response_string, 'UTF-8'))



def render(request, file_name, replace=dict(), status_code=200, status_message='OK', headers = {'Content-type':'text/html'}):
    file_path = os.path.join(request.localserver.TEMPLATE_DIR,file_name)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            for key in replace:
                content = content.replace(key, replace[key])
        return HttpResponse(content, status_code=status_code, status_message=status_message, headers = headers)
    else:
        ##TODO:
        if request.localserver.DEBUG:
            return HttpResponse('<h2 style="color:red">(500) Internal Error: file not found: %s at %s</h2><p>set Server.DEBUG = False to disable this error message </p>'% (file_name, request.localserver.TEMPLATE_DIR), 
            status_code=500, status_message='InternalError')
        else:
            return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')



class Handler(SimpleHTTPRequestHandler):
    
    ## static var
    localserver = None

    def do_GET(self):

        if (self.path[-1]!='/'): self.path+='/'
        
        for path in Handler.localserver.urlpatterns:
            if path.is_equal(self.path):
                parsed_url  = urlparse.urlparse(self.path)
                query       = parse_qs(parsed_url.query)
                url_args    = [] ## TODO: create with urlpatterns
                for key in query:
                    query[key] = query[key][0]
                request = self.create_request(GET = query)

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
                paths = ''
                for path in self.localserver.urlpatterns:
                    paths+= '<li>'+ path.url+'</li>'

                resp = HttpResponse('<h2 style="color:red">(404) Page Not Found</h2><p>supported url patterns:<ol>%s<ol></p>'%paths, 
                status_code=404, status_message='NotFound')
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