import sqlite3
from .constants import FieldTypes as FT


class SQLModel:
    '''SQL database values'''

    fields = {
        'Date': {'req': True, 'type': FT.iso_date_string},
        'Time': {'req': True, 'type': FT.iso_time_string},
        'Distance': {'req': True, 'type': FT.decimal,
                     'min': 0, 'max': 1000, 'inc': .1},
        'Location': {'req': True, 'type': FT.string},
    }

    # create tables if not existing
    create_running_table_command = ('CREATE TABLE IF NOT EXISTS running '
                                    '(date DATE UNIQUE NOT NULL, '
                                    'time TIME NOT NULL, '
                                    'distance REAL NOT NULL, '
                                    'location TEXT NOT NULL, '
                                    'PRIMARY KEY(date))')

    # insert running session in running table
    running_insert_query = ('INSERT INTO running VALUES (:date, '
                            ':time, :distance, :location) ')

    # update running session in running table
    running_update_query = ('UPDATE running SET time=:time, '
                            'distance=:distance, '
                            'location=:location, '
                            'WHERE date=:date')

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

    # only upon first run of the running application
    def create_db_and_tables(self):
        '''Creates database and tables if they don't already exist'''

        self.query(self.create_running_table_command)
