
## '/static/'.split('/') -> ['','static,'']
## as_list -> ['static'], remove all ['']
from . import utils
try:
    import settings
except ImportError:
    utils.create_settings_file()
    import settings


__all__ = [ 'Path' ]

def _url_as_list(url):
    return list(filter(lambda elem: elem!='', url.split('/')))


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

    def compare(self, request, url): ## /some/path = /some/path/

        args = []
        
        ## for static paths
        url_list = _url_as_list(url) 
        if len(url_list) > 0:
            if url_list[0] == _url_as_list(request.localserver.LOCALHOST_STATIC_URL)[0] and self.url == request.localserver.LOCALHOST_STATIC_URL:
                return True, args
            if url_list[0] == _url_as_list(settings.STATIC_URL)[0] and self.url == settings.STATIC_URL:
                return True, args
                

        if self.url == url :
            return True, args
        if len(_url_as_list(self.url)) != len(_url_as_list(url)):
            return False, args
        for i in range(len(_url_as_list(url)) ):
            if _url_as_list(self.url)[i][0] == '<' and _url_as_list(self.url)[i][-1] == '>':
                args.append(_url_as_list(url)[i])
                continue
            if _url_as_list(self.url)[i] != _url_as_list(url)[i]:
                return False, args
        return True, args
    



