
from . import login, logout, authenticate
from ..db.table import Table

from ..response import render, redirect, _render

def _handle_admin_home_page(request):

    error_template = '''\
    <div class="card" style="margin-left:3%;margin-right:3%; padding-top:10px; border-color:rgb(189, 4, 4)">
            <p style="text-align: center; color:rgb(206, 64, 64); font-size:110%">{0}</p>
        </div>
    '''
    if request.user_id is not None:
        user_table = Table.get_table('users', 'auth')

        user = user_table.all.get(id=request.user_id)
        if user['is_admin']:
            return redirect(request, 'home')
            pass ## TODO:
        else: 
            error_message = 'You are authenticated as %s but not autherized to access this page.'%user['username']
            return _render(request, 'localhost-admin.html', request.localserver.LOCALHOST_TEMPLATE_DIR, 
            context={'title':'admin', 'error_message': error_template.format(error_message) }
        )


    if request.method == 'GET':
        return _render(request, 'localhost-admin.html', request.localserver.LOCALHOST_TEMPLATE_DIR, 
            context={'title':'admin'}
        )
    elif request.method == 'POST':

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        ## authenticate
        user_id = authenticate(username, password)
        if user_id is None:
            error_message = 'Authentication failed! check your username and password.'
            return _render(request, 'localhost-admin.html', request.localserver.LOCALHOST_TEMPLATE_DIR, 
                context={'title':'admin', 'username':username, 'error_message': error_template.format(error_message) }
            )
        else:
            login(request, user_id)
            return redirect(request, '/') ## TODO: to admin page

