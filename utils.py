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