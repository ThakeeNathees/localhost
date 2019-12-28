
import sys, os
from distutils.dir_util import copy_tree
import random 

## TODO: use argparse
args = sys.argv

def generage_secret_key():
    characters = ''
    for c in range(ord('a'), ord('z')+1): characters += chr(c)
    for c in range(ord('A'), ord('Z')+1): characters += chr(c)
    for i in range(10): characters += str(i)
    for sym in "!@#$%^&*()+-_=:;?/>.<,{[]}" : characters += sym

    SECRET_KEY_LEN = 50
    secret_key = ''
    for i in range(SECRET_KEY_LEN):
        secret_key += random.choice(characters)
    return secret_key

## localhost init [path]
if len(args) >= 2:
    if args[1] == 'init':
        path = args[2] if len(args) == 3 else os.getcwd()
        if os.path.exists(os.path.join(path, 'server_data')) or os.path.exists(os.path.join(path, 'main.py')):
            raise Exception('init path must not contain server_data/ or main.py')
        copy_tree(os.path.join(os.path.dirname(__file__), 'init'), path)

        ## secret key
        with open( os.path.join(path, 'server_data/settings.py'), 'r' ) as settings_file:
            setting_string = settings_file.read()
        with open( os.path.join(path, 'server_data/settings.py'), 'w' ) as settings_file:
            settings_file.write( setting_string.replace("^^SECRET_KEY^^", generage_secret_key() ) )
    else:
        ## TODO: other args
        print('<usage> : python localhost init [path]')


else:
    print('<usage> : python localhost init [path]')