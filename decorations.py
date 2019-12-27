
## TODO: move login path to settings.py
## also 404 path
from server_data import settings
LOGIN_PATH = 'admin-login'
if hasattr(settings, 'LOGIN_PATH'):
    LOGIN_PATH = settings.__dict__['LOGIN_PATH']

from .response import redirect

def login_required(func):

    def wrapper(*args, **kwargs):
        if len(args) == 0: raise Exception('did you forget the request argument')
        request = args[0]
        if request.user_id is not None:
            return func(*args, **kwargs)
        else:
            return redirect(request, LOGIN_PATH)

    return wrapper
