
## TODO: move login path to settings.py
## also 404 path
try:
    from server_data import settings
except ImportError:
    raise Exception('did you initialize with "python localhost init [path]" ?')

LOGIN_PATH = settings.__dict__['LOGIN_PATH'] if hasattr(settings, 'LOGIN_PATH') else 'admin-login'

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
