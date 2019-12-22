import os, random


def _type_check(*check_list):
    for obj, _type  in check_list:
        if type(_type) == str:
            if type(obj).__name__ != _type:
                if (_type == "Handler"): _type += "(request)"
                raise TypeError( "expected type: %s, called with '%s' of type %s"%( _type, obj, type(obj).__name__ ) )
        else:
            if type(obj) != _type:
                raise TypeError( "expected type: %s, called with %s of type %s" % ( _type, obj, type(obj)) )



def create_settings_file():
    if not os.path.exists( os.path.join(os.getcwd(), 'settings.py') ):
        with open( os.path.join( os.path.dirname(__file__), 'settings.txt' ) ,'r') as local_settings_file:
            settings_string = local_settings_file.read()
        with open( os.path.join(os.getcwd(), 'settings.py'), 'w' ) as settings_file:
            characters = ''
            for c in range(ord('a'), ord('z')+1): characters += chr(c)
            for c in range(ord('A'), ord('Z')+1): characters += chr(c)
            for i in range(10): characters += str(i)
            for sym in "!@#$%^&*()+-_=:;?/>.<,{[]}" : characters += sym

            SECRET_KEY_LEN = 50
            secret_key = ''
            for i in range(SECRET_KEY_LEN):
                secret_key += random.choice(characters)

            settings_file.write(settings_string.replace("^^SECRET_KEY^^", secret_key))

    import settings
    for must_have in ( 'DEBUG', 'SECRET_KEY', 'BASE_DIR', 'TEMPLATE_DIR', 'STATIC_DIR', 'STATIC_URL', 'DB_DIR'):
            if not hasattr(settings, must_have):
                raise Exception('settings file must contain value %s', must_have)
