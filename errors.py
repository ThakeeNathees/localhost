
class Http404(Exception):
    pass


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

