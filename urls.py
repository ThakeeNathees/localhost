
## '/static/'.split('/') -> ['','static,'']
## as_list -> ['static'], remove all ['']
def url_as_list(url):
    return list(filter(lambda elem: elem!='', url.split('/')))


class Path:
    def __init__(self, url, handler, name=''):
        if '//' in url :
            raise Exception('Error: %s is not a valid url', url)
        if url == '' : url = '/'
        if (url[0] != '/'): url = '/'+url
        if not hasattr(handler, '__call__'):
            raise Exception('Error: %s is not callable', handler)

        self.url        = url
        self.handler    = handler
        self.name       = name

    def compare(self, url, request): ## /some/path = /some/path/

        args = []
        
        ## for static paths
        url_list = url_as_list(url) 
        if len(url_list) > 0:
            if url_list[0] == url_as_list(request.localserver.LOCALHOST_STATIC_URL)[0] and self.url == request.localserver.LOCALHOST_STATIC_URL:
                return True, args
            if url_list[0] == url_as_list(request.localserver.STATIC_URL)[0] and self.url == request.localserver.STATIC_URL:
                return True, args
                

        if self.url == url :
            return True, args
        if len(url_as_list(self.url)) != len(url_as_list(url)):
            return False, args
        for i in range(len(url_as_list(url)) ):
            if url_as_list(self.url)[i][0] == '<' and url_as_list(self.url)[i][-1] == '>':
                args.append(url_as_list(url)[i])
                continue
            if url_as_list(self.url)[i] != url_as_list(url)[i]:
                return False, args
        return True, args
    



