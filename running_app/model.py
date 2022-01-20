import sqlite3
from .constants import FieldTypes as FT


class SQLModel:
    '''SQL database values'''

    fields = {
        'Date': {'req': True, 'type': FT.iso_date_string},
        'Time': {'req': True, 'type': FT.time_string},
        'Distance': {'req': True, 'type': FT.decimal},
        'Location': {'req': True, 'type': FT.boolean},
    }

    # create tables if not existing
    create_running_table_command = ('CREATE TABLE IF NOT EXISTS running '
                                    '(date DATE UNIQUE NOT NULL, '
                                    'time TIME NOT NULL, '
                                    'distance REAL NOT NULL, '
                                    'PRIMARY KEY(date))')

    # create or connect to a database
    def __init__(self, database):
        self.connection = sqlite3.connect(database)

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
        except (sqlite3.Error) as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()
            if cursor.description is not None:
                return cursor.fetchall()
