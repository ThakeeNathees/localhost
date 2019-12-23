from hashlib import md5
from time import time
import os, sys


from .db.table import Table, DoesNotExists

try:
    from server_data import settings
except ImportError:
    from .utils import create_settings_file
    create_settings_file()
    from server_data import settings

try:
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    from http.cookies import SimpleCookie
except ImportError:
    print('Error: localhost only supprts for python3')
    sys.exit(1)

## return user id if user exists else None
def authenticate(username, password):
    user_table = Table.get_table('users', 'auth')
    try:
        user = user_table.all.get(username=username, password= md5(password.encode('utf-8')).hexdigest() )
        return user['id']
    except DoesNotExists:
        return None

def login(request, user_id):
    session_id = md5( ( str(user_id) + str(int(time())) ).encode('utf-8')  ).hexdigest()
    request.set_session_id = session_id
    request.user_id = user_id

def logout(request):
    if request.user_id is None:
        return
    session_table = Table.get_table('session_id', 'auth')
    session_table.remove(session_table.all.get(user_id = request.user_id))
    cookie = SimpleCookie()
    cookie['session_id'] = ''
    request.send_header('Set-Cookie', cookie.output(header='', sep=''))
    request.user_id = None
