import os, re

IMAGE_FILE_FORMATS = (
    'jpeg', 'jpg', 'png', ## TODO: add more
)

def _get_404_context(request):
    ctx = dict()
    ctx['error_message'] = '(404) Page Not Found'
    ctx['title'] = '404 NotFound'
    paths = ''
    for path in request.localserver.urlpatterns:
        if not path.url.startswith( request.localserver.STATIC_URL ) and not path.url.startswith( request.localserver.LOCALHOST_STATIC_URL ) : ## url = '/static/'
            paths += '<li>'+ path.url.replace('<', '&lt;').replace('>', '&gt;')  +'</li>'
    paths += '<li>'+ request.localserver.STATIC_URL +'&lt;file_path&gt;</li>'
    ctx['error_content'] = '<p>supported url patterns:<ol>%s<ol></p>'%paths 
    return ctx


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
        if request.localserver.DEBUG:
            format_list = ''
            for img_format in IMAGE_FILE_FORMATS:
                format_list += '<li>%s<li>'%img_format
            return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                    'title':'500 InternalError',
                    'error_message' : '(500) InternalError',
                    'error_content' : '%s file does not exists or not an image file <br>supported image formats<ul>%s<ul>'% (file_path, format_list ),
                }, status_code=500, status_message='InternalError')
        else:
            return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')

def render(request, file_name, context=dict(), status_code=200, status_message='OK', headers = {'Content-type':'text/html'}):
    file_path = os.path.join(request.localserver.TEMPLATE_DIR,file_name)

    ## validate context keys
    for key in context.keys():
        if re.match('^[A-Za-z_][A-Za-z_0-9]*$', key) is None:
            if request.localserver.DEBUG:
                return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                        'title':'500 InternalError',
                        'error_message' : '(500) InternalError',
                        'error_content' : 'invalid key name for render context : "%s"'%key,
                    }, status_code=500, status_message='InternalError')
            else:
                return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')

    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()

            reg_ex_begin = r'{{\s*html_base_begin\s*}}'
            reg_ex_end   = r'{{\s*html_base_end\s*}}'
            count_begin  = len( re.findall(reg_ex_begin, content) )
            count_end    = len( re.findall(reg_ex_end, content) )
            if count_begin >=2 or count_end >=2 : ## more than one extends
                if request.localserver.DEBUG:
                    which = '{{ html_base_begin }}' if count_begin >=2 else '{{ html_base_end }}'
                    return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                            'title':'500 InternalError',
                            'error_message' : '(500) InternalError',
                            'error_content' : 'more than one %s found'%which,
                        }, status_code=500, status_message='InternalError')
                else:
                    return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
            
            if count_begin ^ count_end != 0 :
                if request.localserver.DEBUG:
                    which = '{{ html_base_begin }}' if count_begin >=2 else '{{ html_base_end }}'
                    return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                            'title':'500 InternalError',
                            'error_message' : '(500) InternalError',
                            'error_content' : '{{ html_base_begin }} and {{ html_base_end }} are mismatch',
                        }, status_code=500, status_message='InternalError')
                else:
                    return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
            
            html_base_begin = re.search( reg_ex_begin, content)
            html_base_end   = re.search( reg_ex_end, content)

            if count_begin == 1:

                if (len(content) - len(content.lstrip())) != html_base_begin.start():
                        if request.localserver.DEBUG:
                            return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                                    'title':'500 InternalError',
                                    'error_message' : '(500) InternalError',
                                    'error_content' : '{{ html_base_begin }} must be the at the begining of the file',
                                }, status_code=500, status_message='InternalError')
                        else:
                            return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
                
                if (len(content.rstrip())) != html_base_end.end():
                        if request.localserver.DEBUG:
                            return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                                    'title':'500 InternalError',
                                    'error_message' : '(500) InternalError',
                                    'error_content' : '{{ html_base_end }} must be the at the end of the file',
                                }, status_code=500, status_message='InternalError')
                        else:
                            return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
                
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
                    if request.localserver.DEBUG:
                        return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                                'title':'500 InternalError',
                                'error_message' : '(500) InternalError',
                                'error_content' : 'file %s dosent exists'%request.localserver.BASE_HTML_BEGIN_PATH,
                            }, status_code=500, status_message='InternalError')
                    else:
                        return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
                
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
                    if request.localserver.DEBUG:
                        return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                                'title':'500 InternalError',
                                'error_message' : '(500) InternalError',
                                'error_content' : 'file %s dosent exists'%request.localserver.BASE_HTML_END_PATH,
                            }, status_code=500, status_message='InternalError')
                    else:
                        return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')

            #######################################################################################

            context.update( request.localserver.LOCALHOST_CTX )
            for key in context:
                if (key == 'error_content'): print(context[key])
                content = re.sub(r'{{\s*%s\s*}}'%key, context[key].replace('\\','/'), content)
        return HttpResponse(content, status_code=status_code, status_message=status_message, headers = headers)
    else:
        ##TODO:
        if request.localserver.DEBUG:
            return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                    'title':'500 InternalError',
                    'error_message' : '(500) InternalError',
                    'error_content' : '%s file does not exists'% file_path, ##
                }, status_code=500, status_message='InternalError')
        else:
            return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')

import sys
try:
    from http.server import SimpleHTTPRequestHandler
except ImportError:
    print('Error: localhost only supprts for python3')
    sys.exit(1)



def redirect(request, name_or_path, status_code=307, status_message='REDIRECT',):
    if not isinstance(request, SimpleHTTPRequestHandler): ## instance of Handler
        if request.localserver.DEBUG:
            return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                    'title':'500 InternalError',
                    'error_message' : '(500) InternalError',
                    'error_content' : 'first argument of redirect must me request',
                }, status_code=500, status_message='InternalError')
        else:
            return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
    
    paths = request.localserver.urlpatterns
    for path in paths:
        equal, _ = path.compare(name_or_path)
        if equal or (path.name == name_or_path):
            return Response(status_code=status_code, status_message=status_message, headers={
                    'Location': path.url
                }, is_redirect=True
            )
    if request.localserver.DEBUG:
            return render(request, request.localserver._ERROR_TEMPLATE_PATH, context={
                    'title':'500 InternalError',
                    'error_message' : '(500) InternalError',
                    'error_content' : '%s is an invalid redirect name of path'%name_or_path,
                }, status_code=500, status_message='InternalError')
    else:
        return HttpResponse('<h2>(500) Internal Error</h2>', status_code=500, status_message='InternalError')
            
    
