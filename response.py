import os, re, traceback

from array import array
from .urls import _url_as_list

from . import utils

try:
    from server_data import settings
except ImportError:
    utils.create_settings_file()
    from server_data import settings

from . import auth
from .db.table import Table, DoesNotExists

MEDIA_FILE_FORMAT = {
    ## format : mime/type , is_binary

    ## images
    'jpg'   : ('image/jpg',     True),
    'jpeg'  : ('image/jpeg',    True),
    'jfif'  : ('image/jpeg',    True),
    'pjpeg'  : ('image/jpeg',   True),
    'pjp'  : ('image/jpeg',     True),
    'png'   : ('image/png',     True),
    'gif'   : ('image/gif',     True),
    'bmp'   : ('image/bmp',     True),
    'ico'   : ('image/x-icon',  True),
    'cur'   : ('image/x-icon',  True),
    'svg'   : ('image/svg+xml', True),
    'tif'   : ('image/tiff',    True),
    'tiff'  : ('image/tiff',    True),
    'webp'  : ('image/webp',    True),
    
    ## text files
    'css'   : ( 'text/css',         False ),
    'js'    : ( 'text/javascripts', False ),
    'html'  : ( 'text/html',        False ),
    'csv'   : ( 'text/csv',         False ),
    'txt'   : ('text/plain',        False),
    'json'  : ('text/json',         False),

    ## video
    'mp4'   : ('video/mp4', True),

    ## audio


    ## other binary
    ## binary documents without a specific or known subtype, application/octet-stream should be used.
    'pdf'   : ('application/pdf',   True),
    'ttf'   : ('font/ttf',          True),
    'woff'  : ('font/woff',         True),
    'otf'   : ('font/otf',          True),

}

class Http404(Exception):
    pass


def _get_404_context(request):
    ctx = dict()
    ctx['error_message'] = '(404) Page Not Found'
    ctx['title'] = '404 NotFound'
    paths = ''
    for path in request.localserver.urlpatterns:
        if not path.url.startswith( settings.STATIC_URL ) and not path.url.startswith( request.localserver.LOCALHOST_STATIC_URL ) : ## url = '/static/'
            paths += '<li>'+ path.url.replace('<', '&lt;').replace('>', '&gt;')  +'</li>'
    paths += '<li>'+ settings.STATIC_URL +'&lt;file_path&gt;</li>'
    ctx['error_content'] = '<p>supported url patterns:<ol>%s<ol></p>'%paths 
    return ctx


def _static_handler(request, static_dir, status_code=200, status_message='OK'):
    file_path = os.path.join(static_dir,  '/'.join(_url_as_list(request.path)[1:]  ) ) ## '/static/image.jpg/ -> [  static, image.jpg ]
    
    
    file_format = file_path.split('.')[-1].lower().replace('/', '') ## path/to/media.format/
    if os.path.exists(file_path) and os.path.isfile(file_path):
        if  file_format in MEDIA_FILE_FORMAT.keys():
            mime_type, binary = MEDIA_FILE_FORMAT[file_format]
            read_mode = 'rb' if binary else 'r'
            with open(file_path, read_mode) as file:
                content = file.read()
                if binary:
                    return Response( headers = { 'Content-type': mime_type }, data=content, status_code=status_code, status_message=status_message)
                else:
                    return HttpResponse(content, headers= { 'Content-type': mime_type }, status_code=status_code, status_message=status_message)
        else:
            raise Http404("unknown file type in static : %s"%file_path)
    else:
        raise Http404()


def _handle_static_url_localhost(request):
    return _static_handler(request, request.localserver.LOCALHOST_STATIC_DIR)
def _handle_static_url_developer(request):
    return _static_handler(request, settings.STATIC_DIR)

 
class Response:
    def __init__(self, status_code=200, status_message='OK', headers = {'Content-type':'text/html'}, data=bytes('','UTF-8'), is_redirect=False):
        self.is_redirect        = is_redirect
        self.status_code        = status_code
        self.status_message     = status_message
        self.headers            = headers
        self.data               = data


class HttpResponse(Response):
    def __init__(self, response_string, status_code=200, status_message='OK', headers = {'Content-type':'text/html'}, is_redirect=False):
        utils._type_check(
            (response_string, str), (is_redirect, bool),
            (status_code, int),  (status_message, str), (headers, dict)
        )
        super().__init__(status_code=status_code, status_message=status_message, headers = headers, data=bytes(response_string, 'UTF-8'), is_redirect=False)

class JsonResponse(Response):
        def __init__(self, response_string, status_code=200, status_message='OK', headers = {'Content-type':'application/json'}, is_redirect=False):
            utils._type_check(
                (response_string, str), (is_redirect, bool),
                (status_code, int),  (status_message, str), (headers, dict)
            )
            super().__init__(status_code=status_code, status_message=status_message, headers = headers, data=bytes(response_string, 'UTF-8'), is_redirect=False)

## TODO: static dir -> media dir
def media_response(request, file_name, status_code=200, status_message='OK'):
    utils._type_check(
        (request, 'Handler'), (file_name, str), 
        (status_code, int),  (status_message, str),
    )
    return _static_handler(request, settings.STATIC_DIR, status_code, status_message)

def render(request, file_name, ctx=dict(), status_code=200, status_message='OK', headers = {'Content-type':'text/html'}):
    utils._type_check(
        (request, 'Handler'), (file_name, str), (ctx, dict),
        (status_code, int),  (status_message, str), (headers, dict)
    )
    return _render(request, file_name, settings.TEMPLATE_DIR, ctx, status_code, status_message, headers)

## used for local host rendering
def _render(request, file_name, template_path, context=dict(), status_code=200, status_message='OK', headers = {'Content-type':'text/html'}):
    file_path = os.path.join(template_path, file_name)
    
    ## validate context keys
    for key in context.keys():
        if re.match('^[A-Za-z_][A-Za-z_0-9]*$', key) is None:
            raise Exception('invalid key name for render context : "%s"'%key)

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
                    raise Exception('more than one %s found'%which)
            
            if count_begin ^ count_end != 0 :
                raise Exception( '{{ html_base_begin }} and {{ html_base_end }} are mismatch')
                    
            html_base_begin = re.search( reg_ex_begin, content)
            html_base_end   = re.search( reg_ex_end, content)

            if count_begin == 1:

                if (len(content) - len(content.lstrip())) != html_base_begin.start():
                    raise Exception( '{{ html_base_begin }} must be the at the begining of the file'  )
                
                if (len(content.rstrip())) != html_base_end.end():
                    raise Exception( '{{ html_base_end }} must be the at the end of the file'  )


                ## replace begin
                developer_begin_template_path = os.path.join(settings.TEMPLATE_DIR, request.localserver.BASE_HTML_BEGIN_PATH)
                localhost_begin_template_path = os.path.join(request.localserver.LOCALHOST_TEMPLATE_DIR, request.localserver.BASE_HTML_BEGIN_PATH)
                if os.path.exists(developer_begin_template_path) and os.path.isfile(developer_begin_template_path):
                    with open(developer_begin_template_path, 'r') as file:
                        content = re.sub(reg_ex_begin, file.read(), content)
                elif os.path.exists(localhost_begin_template_path) and os.path.isfile(localhost_begin_template_path):
                    with open(localhost_begin_template_path, 'r') as file:
                        content = re.sub(reg_ex_begin, file.read(), content)
                else:
                    raise Exception( 'file %s dosent exists'%request.localserver.BASE_HTML_BEGIN_PATH  )


                ## replace end
                developer_end_template_path = os.path.join(settings.TEMPLATE_DIR, request.localserver.BASE_HTML_END_PATH)
                localhost_end_template_path = os.path.join(request.localserver.LOCALHOST_TEMPLATE_DIR, request.localserver.BASE_HTML_END_PATH)
                if os.path.exists(developer_end_template_path) and os.path.isfile(developer_end_template_path):
                    with open(developer_end_template_path, 'r') as file:
                        content = re.sub(reg_ex_end, file.read(), content)
                elif os.path.exists(localhost_end_template_path) and os.path.isfile(localhost_end_template_path):
                    with open(localhost_end_template_path, 'r') as file:
                        content = re.sub(reg_ex_end, file.read(), content)
                else:
                    raise Exception( 'file %s dosent exists'%request.localserver.BASE_HTML_END_PATH )


            #######################################################################################
            if 'title' not in context.keys():
                context['title'] = 'localhost'
            context.update( request.localserver.LOCALHOST_CTX )
            for key in context:
                if type(context[key]) == str:
                    context[key] = context[key].replace('\\','/')
                content = re.sub(r'{{\s*%s\s*}}'%key, str(context[key]), content)
            content = re.sub(r'{{\s*[A-Za-z_][A-Za-z_0-9]*\s*}}', '', content) ## clear other replaces words
        return HttpResponse(content, status_code=status_code, status_message=status_message, headers = headers)
    else:
        raise Exception( '%s file does not exists'% file_path )


import sys
try:
    from http.server import SimpleHTTPRequestHandler
except ImportError:
    print('Error: localhost only supprts for python3')
    sys.exit(1)

def reverse(request, name, *args):
    utils._type_check(
        (request, 'Handler'), (name, str)
    )
    for path in request.localserver.paths:
        if path.name == name:
            url = path.url
            for arg in args:
                url = re.sub(r'/<\s*[A-Za-z_][A-Za-z_0-9]*\s*>/', arg, url)
            return path.url
    raise Exception( '%s is an invalid redirect name to reverse'%name )

def redirect(request, name_or_path, status_code=307, status_message='REDIRECT'):
    utils._type_check(
        (request, 'Handler'), (name_or_path, str), (status_code, int), (status_message, str),
    )
    if not isinstance(request, SimpleHTTPRequestHandler): ## instance of Handler
        raise Exception( 'first argument of redirect must me request' )
    
    paths = request.localserver.urlpatterns
    for path in paths:
        equal, _ = path.compare(request, name_or_path)
        if equal or (path.name == name_or_path):
            return Response(status_code=status_code, status_message=status_message, headers={
                    'Location': path.url
                }, is_redirect=True
            )
    raise Exception( '%s is an invalid redirect name or path'%name_or_path )


############### errors #############################

def _error_http404(request):
    if settings.DEBUG:
        return render(request, request.localserver.NOTFOUND404_TEMPLATE_PATH, ctx=request.localserver.NOTFOUND404_GET_CONTEXT(request), status_code=404, status_message='NotFound')
    else:
        return HttpResponse('<h2>(404) Not Found</h2>', status_code=404, status_message='NotFound')
    
def _error_http500(request, error_message, stack_trace=''):
    if settings.DEBUG:
        return render(request, request.localserver._ERROR_TEMPLATE_PATH, ctx={
            'title':'500 InternalError',
            'error_message' : '(500) InternalError',
            'error_content' : error_message+'<br><br>%s' % stack_trace.replace('\n','<br>')
        }, status_code=500, status_message='InternalError')
    else:
        return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
