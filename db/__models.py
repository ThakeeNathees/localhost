import os, csv


from .. import utils
try:
    from server_data import settings
except ImportError:
    utils.create_settings_file()
    from server_data import settings

from .table import Table

class Object: ## a row in csv file

    def __init__(self, for_model):
        if not issubclass(for_model, Model):
            raise Exception('%s is not a subclass of Model'% for_model)
        self.__dict__['for_model']  = for_model
        self.__dict__['fields']     = dict()
        self.__dict__['pk']         = None

        self.__dict__['table_path'] = os.path.join(settings.BASE_DIR, settings.DB_DIR, self.__dict__['for_model'].APP_NAME, self.__dict__['for_model'].__name__.capitalize()+'.csv' )
        self.__dict__['table']      = Table(self.__dict__['table_path'] )

    ## self.uid  = (IntegerField(), value)
    ## self.name = (CharField(...), value)
    def __getattr__(self, key):
        if key == 'pk':
            return self.__dict__['fields'][self.__dict__['pk']][1]

        if key not in self.fields.keys():
            AttributeError('%s object has no attribute %s'%(self.__dict__['for_model'], key))
        return self.__dict__['fields'][key][1]
    
    def _setattr(self, key, field_and_value):
        self.__dict__['fields'][key] = field_and_value

    def __setattr__(self, key, value): ## _trusted -> avoid loop again
        if key == 'pk':
            self.__dict__['pk'] = value
            return value
        for col_name in filter(lambda attrib: isinstance(self.for_model.__dict__[attrib], Field), self.for_model.__dict__):
            if col_name == key:
                self.__dict__['fields'][key][1] = value
                return value
        
        if key == 'id' and key in self.__dict__['fields'].keys():
            self.__dict__['fields'][key][1] = value
        else:
            raise AttributeError('%s object has no attribute %s'%(self.for_model, key))


    def save(self):

        ## validate fields
        for col_name in self.__dict__['fields'].keys():
            field, value = self.__dict__['fields'][col_name]
            field.validate(value)
        
        if not os.path.exists(self.table_path):

            if not os.path.exists(os.path.dirname(self.table_path)):
                os.makedirs(os.path.dirname(self.table_path))

            with open(self.table_path, 'w') as table_file:
                db_writer = csv.writer(table_file, delimiter=',', lineterminator='\n')
                db_writer.writerow(self.__dict__['fields'].keys())

        
        new_row = dict()
        for col_name in self.__dict__['fields'].keys():
            field, value = self.__dict__['fields'][col_name]

            if field.unique and not field.primary_key :
                if self.table.query_set.filter(**{col_name:value}).count() > 0:
                    raise Exception('unique field %s already has the value %s'%(col_name, value))

            if isinstance(field, IntegerField):
                if field.autoincrement:
                    self.__dict__['fields'][col_name][1] = self.table.get_next_autoincrement_value(col_name)
            elif hasattr(field, 'autoincrement'):
                    raise Exception('only integer fields can autoincrement')
            
            new_row[col_name] = value
        
        pk_name  = self.__dict__['pk']
        pk_value = self.__dict__['fields'][pk_name][1]

        if self.table.query_set.filter(**{pk_name:pk_value}).count() == 0:
            self.table.insert(new_row)
        else:
            obj = self.table.query_set.filter(**{pk_name:pk_value})[0] ## already exists
            self.table.update(pk_name, obj)

            
        



class Model:
    APP_NAME = None ## ..../db/appname/table
    @classmethod
    def create(cls, save=True, **kwargs):
        obj = Object(cls)
        for col_name in filter(lambda attrib: isinstance(cls.__dict__[attrib], Field), cls.__dict__):
            field = cls.__dict__[col_name]

            value = None
            if col_name in kwargs.keys():
                value = kwargs[col_name]
            else:
                if field.default is not None:
                    value = field.default
                else:
                    if not field.null :
                        if isinstance(field, IntegerField) and field.autoincrement:
                            pass
                        else: raise Exception("required keyword argument '%s' is not proviede" % col_name)

            obj._setattr(col_name, [field, value] )
            if field.primary_key:
                if obj.pk is None:
                    obj.pk = col_name
                else:
                    raise Exception('a model can\'t have multiple primary key')

        if obj.pk is None:
            obj._setattr('id', [IntegerField(autoincrement=True, primary_key=True), 0] )
            obj.pk = 'id'
            obj.id = obj.__dict__['table'].get_next_autoincrement_value('id')
        if save:
            obj.save()

class Field:
    def __init__(self, default=None, null=False, unique=False, primary_key=False):
        self.default        = default
        self.null           = null
        self.unique         = unique
        self.primary_key    = primary_key

        if self.primary_key: self.unique = True

    def validate(self, value):
        pass

class IntegerField(Field):
    def __init__(self, autoincrement=False, default=None, null=False, unique=False, primary_key=False):
        super().__init__(default=default, null=null, unique=unique, primary_key=primary_key)
        self.autoincrement = autoincrement
    
    def validate(self, value):
        if value is None and self.autoincrement:
            pass
        elif type(value) != int:
            raise TypeError("value '%s' is not an integer"%value)


class CharField(Field):
    def __init__(self, max_length, default=None, null=False, unique=False, primary_key=False):
        super().__init__(default=default, null=null, unique=unique, primary_key=primary_key)
        self.max_length = max_length
    
    def validate(self, value):
        if type(value) != str:
            raise TypeError("value %s is not a string"% value)
        if len(value) > self.max_length:
            raise Exception("%s length is greater then max_length(%s)"% (value, self.max_length))
        

class TextField(Field):
    def __init__(self, default=None, null=False, unique=False, primary_key=False):
        super().__init__(default=default, null=null, unique=unique, primary_key=primary_key)
    
    def validate(self, value):
        if type(value) != str:
            raise TypeError("value %s is not a string"% value)

## TODO: image field, email field, file field

