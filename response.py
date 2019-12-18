import os

IMAGE_FILE_FORMATS = (
    'jpeg', 'jpg', 'png', ## TODO: add more
)

def _get_404_context(request):
    ctx = dict()
    ctx['{{ error_message }}'] = '(404) Page Not Found'
    ctx['{{ title }}'] = '404 NotFound'
    paths = ''
    for path in request.localserver.urlpatterns:
        if not path.url.startswith( request.localserver.STATIC_URL ) and not path.url.startswith( request.localserver.LOCALHOST_STATIC_URL ) : ## url = '/static/'
            paths += '<li>'+ path.url.replace('<', '&lt;').replace('>', '&gt;')  +'</li>'
    paths += '<li>'+ request.localserver.STATIC_URL +'&lt;file_path&gt;</li>'
    ctx['{{ error_content }}'] = '<p>supported url patterns:<ol>%s<ol></p>'%paths 
    return ctx


class Response:
    def __init__(self, status_code=200, status_message='OK', headers = {'Content-type':'text/html'}, data=bytes('','UTF-8')):
        self.status_code        = status_code
        self.status_message     = status_message
        self.headers            = headers
        self.data               = data


class HttpResponse(Response):
    def __init__(self, response_string, status_code=200, status_message='OK', headers = {'Content-type':'text/html'}):
        super().__init__(status_code=status_code, status_message=status_message, headers = headers, data=bytes(response_string, 'UTF-8'))



def image_response(request, file_name, status_code=200, status_message='OK'):
    file_path = os.path.join(request.localserver.STATIC_DIR, file_name)

    if os.path.exists(file_path) and os.path.isfile(file_path) and file_name.split('.')[-1].lower() in IMAGE_FILE_FORMATS :
        with open(file_path, 'rb') as file:
            content = file.read()
        return Response(status_code=200, status_message='OK', headers = {'Content-type':'image/%s'%file_name.split('.')[-1].lower()}, data=content)
    else:
        if request.localserver.DEBUG:
             return render(request, request.localserver._ERROR_TEMPLATE_PATH, replace={
                    '{{ title }}':'500 InternalError',
                    '{{ error_message }}' : '(500) InternalError',
                    '{{ error_content }}' : '%s file does not exists'% file_path,
                }, status_code=500, status_message='InternalError')
        else:
            return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')

def render(request, file_name, replace=dict(), status_code=200, status_message='OK', headers = {'Content-type':'text/html'}):
    file_path = os.path.join(request.localserver.TEMPLATE_DIR,file_name)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            replace.update( request.localserver.LOCALHOST_CTX )
            for key in replace:
                content = content.replace(key, replace[key])
        return HttpResponse(content, status_code=status_code, status_message=status_message, headers = headers)
    else:
        ##TODO:
        if request.localserver.DEBUG:
            return render(request, request.localserver._ERROR_TEMPLATE_PATH, replace={
                    '{{ title }}':'500 InternalError',
                    '{{ error_message }}' : '(500) InternalError',
                    '{{ error_content }}' : '%s file does not exists'% file_path, ##
                }, status_code=500, status_message='InternalError')
        else:
            return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')

