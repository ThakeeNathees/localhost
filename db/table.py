import os, csv
from tempfile import NamedTemporaryFile
import shutil

class QuerySet:
    def __init__(self):
        self.rows = []
        
    def append(self, row):
        self.rows.append(row)
    
    def count(self):
        return len(self.rows)

    def filter(self, **kwargs):
        query_set = QuerySet()
        for row in self.rows:
            for key in kwargs.keys():
                if str(kwargs[key]) != row[key]:
                    break
            else:
                query_set.append(row)
        return query_set
    
    def __getitem__(self, key):
        return self.rows[key]

class Table:

    def __init__(self, table_path):
        self.table_path = table_path
        self.query_set = QuerySet()
        self.fieldnames = None

        with open(self.table_path, 'r') as table_file:
            db_reader = csv.reader(table_file, delimiter=',')
            for row in db_reader:
                self.fieldnames = list(row)
                break

        with open(self.table_path, 'r') as table_file:
            db_reader = csv.DictReader(table_file)
            for row in db_reader:
                if self.fieldnames is None:
                    self.fieldnames = list(row)
                self.query_set.append(row)
        
    
    def get_next_autoincrement_value(self, col_name):
        val = 0
        for row in self.query_set.rows:
            if int(row[col_name]) >= val:
                val = int(row[col_name]) + 1
        return val

    def insert(self, new_row):
        with open(self.table_path, 'a') as table_file:
            db_writer = csv.DictWriter(table_file, fieldnames=self.fieldnames, lineterminator='\n')
            db_writer.writerow(new_row)

    def update(self, pk_name, obj):
        tempfile = NamedTemporaryFile(mode='w', delete=False)
                
        with open(self.table_path, 'r') as table_file, tempfile:
            db_reader = csv.DictReader(table_file, fieldnames=self.fieldnames,  lineterminator='\n')
            db_writer = csv.DictWriter(tempfile, fieldnames=self.fieldnames,  lineterminator='\n')
            for row in db_reader:
                if row[pk_name] == obj[pk_name]:
                    for key in obj.keys():
                        row[key] = obj[key]
                db_writer.writerow(row)
        
        shutil.move(tempfile.name, self.table_path)