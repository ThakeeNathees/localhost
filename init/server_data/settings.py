
import os

## directory of server data
SERVER_DATA_DIR = os.path.dirname(os.path.abspath(__file__))

## Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(SERVER_DATA_DIR)

## keep the secret key secret!
SECRET_KEY = '^^SECRET_KEY^^'

DEBUG = True

TEMPLATE_DIR = os.path.join(SERVER_DATA_DIR, 'templates')

STATIC_DIR   = os.path.join(SERVER_DATA_DIR, 'static')
STATIC_URL   = '/static/'

## USE_ADMIN_PAGE   = True      ## set false if you don't want to
## ADMIN_URL        = '/admin/'

DB_DIR       = os.path.join(SERVER_DATA_DIR, 'db')

## set your name or path for custom login path
## LOGIN_PATH = 'admin-login' ## path or name for login url

## set these values for your custom 404 page
## ERROR_TEMPLATE_NAME       = 'localhost/error.html'
## NOTFOUND404_TEMPLATE_NAME = 'localhost/error.html'
## NOTFOUND404_GET_CONTEXT   = lambda request : return { 'context_name' : 'context_value' }

## BASE_HTML_BEGIN_TEMPLATE_NAME  = 'localhost/base-begin.html'
## BASE_HTML_END_TEMPLATE_NAME    = 'localhost/base-end.html'