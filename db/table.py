
import csv, os

from .. import utils
try:
    from server_data import settings
except ImportError:
    utils.create_settings_file()
    from server_data import settings

class DoesNotExists(Exception):
    pass

class QuerySet:
    def __init__(self):
        self.rows = []

    def __getitem__(self, key):
        return self.rows[key]
    
    def append(self, row): ## validate
        self.rows.append(row)

    def __iter__(self):
        self.n = -1
        return self

    def __next__(self):
        if self.n+1 < self.rows.__len__():
            self.n += 1
            return self.rows[self.n]
        else:
            raise StopIteration
    
    def __str__(self):
        ret = ''
        if len(self.rows) == 0:
            return ret

        width = dict()
        for key in self.rows[0].keys():
            width[key] = len(key)
            for row in self.rows:
                width[key] = max( width[key], len(str(row[key])))
        
        ret+= '+'
        for key in width.keys():
            ret += '-'*width[key]+'+' 
        ret += '\n|'
        for key in width.keys():
            ret+= '%s%s' % (key, ' '*(width[key]-len(key))) + '|'
        ret+= '\n+'
        for key in width.keys():
            ret+=  '-'*width[key]+'+'
            
        for row in self.rows:
            ret+= '\n|'
            for key in width.keys():
                ret+=  '%s%s' % (row[key], ' '*(width[key]-len(str(row[key])))) + '|'
        
        ret+= '\n+'
        for key in width.keys():
            ret+='-'*width[key]+'+'
        return ret
    
    def __len__(self):
        return len(self.rows)
        
    def exists(self, **kwargs):
        return len(self.filter(**kwargs)) > 0
    
    def filter(self, **kwargs):
        ret = QuerySet()
        for row in self.rows:
            for key in kwargs:
                if row[key] != kwargs[key]:
                    break
            else:
                ret.append(row)
        return ret
    
    def get(self, **kwargs):
        ret = self.filter(**kwargs)
        if (len(ret)) == 0:
            raise DoesNotExists('Query object not found')
        elif (len(ret)) > 1:
            raise Exception('multiple Query objects found for get - use filter')
        return ret[0]

class Table:

    ## dict of tables, name : 'appname/tablename'
    TABLES = dict()

    @staticmethod
    def get_table(table_name, app_name):
        key = table_name+'/'+app_name
        if key not in Table.TABLES.keys():
            table = Table.load(table_name, app_name)
            Table.TABLES[ key ] = table
        return Table.TABLES[ key ]
            

    def __init__(self, table_name, app_name):
        self.table_name = table_name
        self.app_name   = app_name
        self.all        = QuerySet()
        self.table_path = os.path.join(app_name, table_name+'.csv')
        self.collumns   = dict(id=[int,1])
        pass ## use Table.create() method

    def __str__(self):
        return str(self.all)
        
    @staticmethod
    def exists(table_name, app_name):
        return os.path.exists( os.path.join(settings.DB_DIR, app_name, table_name+'.csv') )
    
    @staticmethod
    def create(table_name, app_name, **kwargs):
        self = Table(table_name, app_name)
        self.collumns.update(kwargs)


        write = False
        if not os.path.exists( os.path.join(settings.DB_DIR, self.table_path) ):
            if not os.path.exists( os.path.dirname( os.path.join(settings.DB_DIR, self.table_path )) ):
                os.makedirs(os.path.dirname( os.path.join(settings.DB_DIR, self.table_path )))
            write = True
        else:
            write = input('table %s already exists, override it [y/n] '%self.table_name).lower() =='y'
        
        if write:
            with open(  os.path.join(settings.DB_DIR, self.table_path ), 'w') as table_file:
                db_writer = csv.DictWriter(table_file, fieldnames=self.collumns.keys(), lineterminator='\n')
                db_writer.writeheader()

                row_1 = dict()
                for key in self.collumns.keys():
                    row_1.update( { key: self.collumns[key][0].__name__ } )
                db_writer.writerow(row_1)

                row_2 = dict()
                for key in self.collumns.keys():
                    row_2.update( { key: self.collumns[key][1] } )
                db_writer.writerow(row_2)
            
            for key in self.collumns.keys(): ## type convert
                if self.collumns[key][1] is not None:
                    self.collumns[key][1] = self.collumns[key][0]( self.collumns[key][1] )
                
        return self

    @staticmethod
    def load(table_name, app_name):
        self = Table(table_name, app_name)

        with open(os.path.join(settings.DB_DIR, self.table_path), 'r') as table_file:
            db_reader = csv.DictReader(table_file,  lineterminator='\n')
            line_num = 0
            dtypes = None; defaults = None
            for row in db_reader:
                if line_num == 0: ## data type
                    dtypes = row
                elif line_num == 1: ## default
                    defaults = row

                    for key in dtypes.keys():
                        if dtypes[key] == 'bool'    : dtypes[key] = bool
                        if dtypes[key] == 'int'     : dtypes[key] = int
                        if dtypes[key] == 'float'   : dtypes[key] = float
                        if dtypes[key] == 'str'     : dtypes[key] = str

                        if defaults[key] != '':
                            defaults[key] = dtypes[key](defaults[key])
                        else:
                            defaults[key] = None
                        self.collumns[key] = [ dtypes[key], defaults[key] ]
                else:
                    for key in self.collumns.keys():
                        row[key] = self.collumns[key][0]( row[key] )
                    self.collumns['id'][1] = row['id'] + 1
                    self.all.append(row)
                    
                line_num += 1
        return self       
    
    def insert(self, **kwargs):
        new_row = dict()
        if 'id' in kwargs.keys():
            raise Exception("id updated automatically don't use")

        for key in self.collumns.keys():
            if key in kwargs.keys():
                new_row[key] = kwargs[key]
            else:
                if self.collumns[key][1] is None:
                    raise Exception( "expected keyword argement '%s' is not proviede" % key )
                new_row[key] = self.collumns[key][1]

        self.all.append( csv.OrderedDict(new_row) ) ## TODO::
        self.collumns['id'][1] += 1
    
    def remove(self, row):
        self.all.rows.remove(row)
                
    
    def save(self):
         with open(  os.path.join(settings.DB_DIR, self.table_path ), 'w') as table_file:
            db_writer = csv.DictWriter(table_file, fieldnames=self.collumns.keys(), lineterminator='\n')
            db_writer.writeheader()

            dtypes = dict()
            for key in self.collumns.keys():
                dtypes[key] = self.collumns[key][0].__name__
            db_writer.writerow(dtypes)
            defaults = dict()
            for key in self.collumns.keys():
                defaults[key] = self.collumns[key][1]
            db_writer.writerow(defaults)

            for row in self.all:
                db_writer.writerow(row)

        
        