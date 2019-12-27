
## '/static/'.split('/') -> ['','static,'']
## as_list -> ['static'], remove all ['']
from . import utils
try:
    from server_data import settings
except ImportError:
    utils.create_settings_file()
    from server_data import settings

import re

__all__ = [ 'path' ]

def _url_as_list(url):
    return list(filter(lambda elem: elem!='', url.split('/')))

def path(url, handler, name=''): ## for a django like interface
    return Path(url, handler, name=name)

class Path:
    def __init__(self, url, handler, name=''):
        utils._type_check(
            (url, str),
            (handler, 'function'),
            (name, str)
        )
        if '//' in url :
            raise Exception('Error: %s is not a valid url', url)
        if url == '' : url = '/'
        if (url[0] != '/'): url = '/'+url
        if not hasattr(handler, '__call__'):
            raise Exception('Error: %s is not callable', handler)

        self.url        = url
        self.handler    = handler
        self.name       = name

    def compare(self, request, url): ## /some/path/<arg1>/ = /some/path/2

        args = []
        
        ## for static paths
        url_list = _url_as_list(url) 
        if len(url_list) > 0:
            if url_list[0] == _url_as_list(request.localserver.LOCALHOST_STATIC_URL)[0] and self.url == request.localserver.LOCALHOST_STATIC_URL:
                return True, args
            if url_list[0] == _url_as_list(settings.STATIC_URL)[0] and self.url == settings.STATIC_URL:
                return True, args
          
        list_self  = _url_as_list(self.url)
        list_other = _url_as_list(url)
        if self.url == url :
            return True, args
        if len(list_self) != len(list_other):
            return False, args
        for i in range(len(list_other)):
            if list_self[i][0] == '<' and list_self[i][-1] == '>':
                args.append(list_other[i])
                continue
            if re.match('^'+list_self[i]+'$', list_other[i]) is None:
                return False, args
        return True, args
    



