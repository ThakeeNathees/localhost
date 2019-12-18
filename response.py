import os

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

