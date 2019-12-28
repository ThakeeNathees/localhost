
from . import login, logout, authenticate
from ..db import Table

from ..response import render, redirect, reverse

def _is_user_admin(user_id):
    if user_id is None:
        return False
    user_table = Table.get_table('users', 'auth')
    user = user_table.all.get(id=user_id)
    return user['is_admin']

def _handle_admin_home_page(request):
    if not _is_user_admin(request.user_id):
        return redirect(request, 'admin-login')
    
    ## render page
    title_template = '''\
    <div style="background-color: rgb(115, 150, 175); padding:2px; padding-left:5px; margin-top:40px">
        <p style="color: white; margin:2px; font-size:110%"> <b>{0}</b></p>
    </div>
    '''
    table_template = '''\
    <a href="{0}" style="text-decoration:none; color:rgb(91, 124, 148); margin:2px; font-size:120%; padding-left: 15px;"><b>{1}</b></a>
    <a href="{2}" style="text-decoration:none; color:rgb(91, 124, 148); font-size:120%; float:right; padding-right:20px">Add</a>
    <hr style="margin:2px">
    '''

    admin_body = ''
    ## register auth
    admin_body += title_template.format('Authentication') 
    admin_body += table_template.format(reverse(request, 'admin-home')+'auth/users/','Users','') 
    admin_body += table_template.format(reverse(request, 'admin-home')+'auth/sessions', 'Sessions', '')

    ## TODO: add other registered apps
    ## TODO: after createing forms add 'add' url

    return render(request, 'localhost/admin/home.html', {'admin_body': admin_body} )

def _handle_admin_table_page(request, app_name, table_name):
    if not _is_user_admin(request.user_id):
        return redirect(request, 'admin-login')

    table = Table.get_table(table_name, app_name)
    table_head = ''
    table_body = ''

    for col_name in table.collumns.keys():
        table_head += '<th scope="col">%s</th>\n'% col_name
    
    for row in table.all:
        table_body += '<tr>'
        for key in row.keys():
            if key == 'id': table_body += '<th scope="row">%s</th>\n' % row[key]
            else: table_body += '<td>%s</td>\n' % row[key]
        table_body += '</tr>'

    return render(request, 'localhost/admin/table.html', {
        'table_head' : table_head, 
        'table_body' : table_body
    })

def _handle_admin_logout_page(request):
    logout(request)
    return render(request, 'localhost/base.html', ctx={
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
            return render(request, 'localhost/admin/login.html', 
            ctx={'title':'admin', 'error_message': error_template.format(error_message) }
        )


    if request.method == 'GET':
        return render(request, 'localhost/admin/login.html', 
            ctx={'title':'admin'}
        )
    elif request.method == 'POST':

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        ## authenticate
        user_id = authenticate(username, password)
        if not _is_user_admin(user_id):
            error_message = 'Authentication failed! check your username and password.'
            return render(request, 'localhost/admin/login.html', 
                ctx={'title':'admin', 'username':username, 'error_message': error_template.format(error_message) }
            )
        else:
            login(request, user_id)
            return redirect(request, 'admin-home')
            
