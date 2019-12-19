import os, re, traceback

IMAGE_FILE_FORMATS = (
    'jpeg', 'jpg', 'png', ## TODO: add more
)

MEDIA_FILE_FORMAT = {
    ## format : mime/type , is_binary


    ## images
    'jpg'   : ('image/jpg',  True),
    'jpeg'  : ('image/jpeg', True),
    'jfif'  : ('image/jpeg', True),
    'pjpeg'  : ('image/jpeg', True),
    'pjp'  : ('image/jpeg', True),
    'png'   : ('image/png',  True),
    'gif'   : ('image/gif',  True),
    'bmp'   : ('image/bmp',  True),
    'ico'   : ('image/x-icon',  True),
    'cur'   : ('image/x-icon',  True),
    'svg'   : ('image/svg+xml',  True),
    'tif'   : ('image/tiff',  True),
    'tiff'  : ('image/tiff',  True),
    'webp'  : ('image/webp',  True),

    
    ## text files
    'css'   : ( 'text/css', False ),
    'js'    : ( 'text/javascripts', False ),
    'html'  : ( 'text/html', False ),
    'csv'   : ( 'text/csv    ', False ),
    'txt'   : ('text/plain', False),
    'json'  : ('text/json', False),

    ## video
    'mp4'   : ('video/mp4', True),

    ## audio


    ## other binary
    ## binary documents without a specific or known subtype, application/octet-stream should be used.
    'pdf'   : ('application/pdf', True),
    'ttf'   : ('font/ttf', True),
    'woff'  : ('font/woff', True),
    'otf'   : ('font/otf', True),



}

from .errors import _get_404_context

class Response:
    def __init__(self, status_code=200, status_message='OK', headers = {'Content-type':'text/html'}, data=bytes('','UTF-8'), is_redirect=False):
        self.is_redirect        = is_redirect
        self.status_code        = status_code
        self.status_message     = status_message
        self.headers            = headers
        self.data               = data


class HttpResponse(Response):
    def __init__(self, response_string, status_code=200, status_message='OK', headers = {'Content-type':'text/html'}, is_redirect=False):
        super().__init__(status_code=status_code, status_message=status_message, headers = headers, data=bytes(response_string, 'UTF-8'), is_redirect=False)

class JsonResponse(Response):
        def __init__(self, response_string, status_code=200, status_message='OK', headers = {'Content-type':'application/json'}, is_redirect=False):
            super().__init__(status_code=status_code, status_message=status_message, headers = headers, data=bytes(response_string, 'UTF-8'), is_redirect=False)

def image_response(request, file_name, status_code=200, status_message='OK'):
    file_path = os.path.join(request.localserver.STATIC_DIR, file_name)

    if os.path.exists(file_path) and os.path.isfile(file_path) and file_name.split('.')[-1].lower() in IMAGE_FILE_FORMATS :
        with open(file_path, 'rb') as file:
            content = file.read()
        return Response(status_code=200, status_message='OK', headers = {'Content-type':'image/%s'%file_name.split('.')[-1].lower()}, data=content)
    else:
        try:
            raise Exception('%s file does not exists or not an image file'% file_path)
        except:
            format_list = ''
            for img_format in IMAGE_FILE_FORMATS:
                format_list += '<li>%s<li>'%img_format
            return _error_http500(request, '%s file does not exists or not an image file <br>supported image formats<ul>%s<ul>'% (file_path, format_list ), traceback.format_exc())

def _media_response(request, file_name, static_dir, status_code=200, status_message='OK'):
    pass

def render(request, file_name, context=dict(), status_code=200, status_message='OK', headers = {'Content-type':'text/html'}):
    return _render(request, file_name, request.localserver.TEMPLATE_DIR, context, status_code, status_message, headers)

## used for local host rendering
def _render(request, file_name, template_path, context=dict(), status_code=200, status_message='OK', headers = {'Content-type':'text/html'}):
    file_path = os.path.join(template_path, file_name)
    
    ## validate context keys
    for key in context.keys():
        if re.match('^[A-Za-z_][A-Za-z_0-9]*$', key) is None:
            try:
                raise Exception('invalid key name for render context : "%s"'%key)
            except:
                return _error_http500(request, 'invalid key name for render context : "%s"'%key,traceback.format_exc())

    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()

            reg_ex_begin = r'{{\s*html_base_begin\s*}}'
            reg_ex_end   = r'{{\s*html_base_end\s*}}'
            count_begin  = len( re.findall(reg_ex_begin, content) )
            count_end    = len( re.findall(reg_ex_end, content) )
            if count_begin >=2 or count_end >=2 : ## more than one extends
                if re.match('^[A-Za-z_][A-Za-z_0-9]*$', key) is None:
                    which = '{{ html_base_begin }}' if count_begin >=2 else '{{ html_base_end }}'
                    try:
                        raise Exception('more than one %s found'%which)
                    except:
                        return _error_http500(request, 'more than one %s found'%which, traceback.format_exc())
            
            if count_begin ^ count_end != 0 :
                try:
                    raise Exception( '{{ html_base_begin }} and {{ html_base_end }} are mismatch')
                except:
                    return _error_http500(request, '{{ html_base_begin }} and {{ html_base_end }} are mismatch', traceback.format_exc())
                    
            html_base_begin = re.search( reg_ex_begin, content)
            html_base_end   = re.search( reg_ex_end, content)

            if count_begin == 1:

                if (len(content) - len(content.lstrip())) != html_base_begin.start():
                    try:
                        raise Exception( '{{ html_base_begin }} must be the at the begining of the file'  )
                    except:
                        return _error_http500(request,'{{ html_base_begin }} must be the at the begining of the file', traceback.format_exc())
                
                if (len(content.rstrip())) != html_base_end.end():
                    try:
                        raise Exception( '{{ html_base_end }} must be the at the end of the file'  )
                    except:
                        return _error_http500(request,  '{{ html_base_end }} must be the at the end of the file', traceback.format_exc())

                ## replace begin
                developer_begin_template_path = os.path.join(request.localserver.TEMPLATE_DIR, request.localserver.BASE_HTML_BEGIN_PATH)
                localhost_begin_template_path = os.path.join(request.localserver.LOCALHOST_TEMPLATE_DIR, request.localserver.BASE_HTML_BEGIN_PATH)
                if os.path.exists(developer_begin_template_path) and os.path.isfile(developer_begin_template_path):
                    with open(developer_begin_template_path, 'r') as file:
                        content = re.sub(reg_ex_begin, file.read(), content)
                elif os.path.exists(localhost_begin_template_path) and os.path.isfile(localhost_begin_template_path):
                    with open(localhost_begin_template_path, 'r') as file:
                        content = re.sub(reg_ex_begin, file.read(), content)
                else:
                    try:
                        raise Exception( 'file %s dosent exists'%request.localserver.BASE_HTML_BEGIN_PATH  )
                    except:
                        return _error_http500(request,  'file %s dosent exists'%request.localserver.BASE_HTML_BEGIN_PATH, traceback.format_exc())

                ## replace end
                developer_end_template_path = os.path.join(request.localserver.TEMPLATE_DIR, request.localserver.BASE_HTML_END_PATH)
                localhost_end_template_path = os.path.join(request.localserver.LOCALHOST_TEMPLATE_DIR, request.localserver.BASE_HTML_END_PATH)
                if os.path.exists(developer_end_template_path) and os.path.isfile(developer_end_template_path):
                    with open(developer_end_template_path, 'r') as file:
                        content = re.sub(reg_ex_end, file.read(), content)
                elif os.path.exists(localhost_end_template_path) and os.path.isfile(localhost_end_template_path):
                    with open(localhost_end_template_path, 'r') as file:
                        content = re.sub(reg_ex_end, file.read(), content)
                else:
                    try:
                        raise Exception( 'file %s dosent exists'%request.localserver.BASE_HTML_END_PATH )
                    except:
                        return _error_http500(request,  'file %s dosent exists'%request.localserver.BASE_HTML_END_PATH, traceback.format_exc())

            #######################################################################################
            if 'title' not in context.keys():
                context['title'] = 'localhost'
            context.update( request.localserver.LOCALHOST_CTX )
            for key in context:
                content = re.sub(r'{{\s*%s\s*}}'%key, context[key].replace('\\','/'), content)
        return HttpResponse(content, status_code=status_code, status_message=status_message, headers = headers)
    else:
        try:
            raise Exception( '%s file does not exists'% file_path )
        except:
            return _error_http500(request, '%s file does not exists'% file_path, traceback.format_exc())

import sys
try:
    from http.server import SimpleHTTPRequestHandler
except ImportError:
    print('Error: localhost only supprts for python3')
    sys.exit(1)



def redirect(request, name_or_path, status_code=307, status_message='REDIRECT',):
    if not isinstance(request, SimpleHTTPRequestHandler): ## instance of Handler
        try:
            raise Exception( 'first argument of redirect must me request' )
        except:
            return _error_http500(request, 'first argument of redirect must me request', traceback.format_exc())
    
    paths = request.localserver.urlpatterns
    for path in paths:
        equal, _ = path.compare(name_or_path)
        if equal or (path.name == name_or_path):
            return Response(status_code=status_code, status_message=status_message, headers={
                    'Location': path.url
                }, is_redirect=True
            )
    try:
        raise Exception( '%s is an invalid redirect name of path'%name_or_path )
    except:
        return _error_http500(request, '%s is an invalid redirect name of path'%name_or_path, traceback.format_exc())


############### errors #############################

def _error_http404(request):
    if request.localserver.DEBUG:
        return render(request, request.localserver.NOTFOUND404_TEMPLATE_PATH, context=request.localserver.NOTFOUND404_GET_CONTEXT(request), status_code=404, status_message='NotFound')
    else:
        return HttpResponse('<h2>(404) Not Found</h2>', status_code=404, status_message='NotFound')
    
def _error_http500(request, error_message, stack_trace=''):
    if request.localserver.DEBUG:
        return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
            'title':'500 InternalError',
            'error_message' : '(500) InternalError',
            'error_content' : error_message+'<br>%s' % stack_trace.replace('\n','<br>')
        }, status_code=500, status_message='InternalError')
    else:
        return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
