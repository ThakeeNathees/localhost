from . import utils
try:
    from server_data import settings
except ImportError:
    utils.create_settings_file()
    from server_data import settings

from .db.table import Table

TABLES  = dict(

    auth = dict( ## app name

        users = dict(
            columns    = dict(
                username = [str, None],
                password = [str, None],
                is_admin = [bool, False],
            )
        ),
        
        sessions = dict(
            columns    = dict(
                session_id = [int, None],
                user_id    = [int, None]
            )
        ),

    )
)

def create_tables():
    for app_name in TABLES:
        for table_name in TABLES[app_name]:
            columns = TABLES[app_name][table_name]['columns']
            if not Table.exists(table_name, app_name):
                table = Table.create(table_name, app_name, **columns)
                table.save()

