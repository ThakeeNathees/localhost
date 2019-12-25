
from . import login, logout, authenticate
from ..db.table import Table

from ..response import render, redirect, _render, reverse

def _is_user_admin(user_id):
    if user_id is None:
        return False
    user_table = Table.get_table('users', 'auth')
    user = user_table.all.get(id=user_id)
    return user['is_admin']

def _handle_admin_home_page(request):
    if not _is_user_admin(request.user_id):
        return redirect(request, 'admin-login')

    return _render(request, 'localhost-admin-home.html', request.localserver.LOCALHOST_TEMPLATE_DIR )

def _handle_admin_logout_page(request):
    logout(request)
    return _render(request, 'localhost-base.html',  request.localserver.LOCALHOST_TEMPLATE_DIR, ctx={
            'content_body': '''<p style="color:rgb(128, 128, 128); font-size:180%">Logged Out</p>
            <p>Thanks for spending some quality time with the Web site today.<p>
            <a href={0} style="text-decoration:none; color:#5e89a8;">Login again</a>
            '''.format(reverse(request, 'admin-login'))
        })

def _handle_admin_login_page(request):

    error_template = '''\
    <div class="card" style="margin-left:3%;margin-right:3%; padding-top:10px; border-color:rgb(189, 4, 4)">
        <p style="text-align: center; color:rgb(206, 64, 64);">{0}</p>
    </div>
    '''
    if request.user_id is not None:
        user_table = Table.get_table('users', 'auth')

        user = user_table.all.get(id=request.user_id)
        if user['is_admin']:
            return redirect(request, 'admin-home')
        else: 
            error_message = 'You are authenticated as "%s" but not autherized to access this page.'%user['username']
            return _render(request, 'localhost-admin-login.html', request.localserver.LOCALHOST_TEMPLATE_DIR, 
            ctx={'title':'admin', 'error_message': error_template.format(error_message) }
        )


    if request.method == 'GET':
        return _render(request, 'localhost-admin-login.html', request.localserver.LOCALHOST_TEMPLATE_DIR, 
            ctx={'title':'admin'}
        )
    elif request.method == 'POST':

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        ## authenticate
        user_id = authenticate(username, password)
        if not _is_user_admin(user_id):
            error_message = 'Authentication failed! check your username and password.'
            return _render(request, 'localhost-admin-login.html', request.localserver.LOCALHOST_TEMPLATE_DIR, 
                ctx={'title':'admin', 'username':username, 'error_message': error_template.format(error_message) }
            )
        else:
            login(request, user_id)
            return redirect(request, 'admin-home')
            
