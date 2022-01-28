import sqlite3
from .constants import FieldTypes as FT


class SQLModel:
    '''SQL database values'''

    fields = {
        'Date': {'req': True, 'type': FT.iso_date_string},
        'Time': {'req': True, 'type': FT.iso_time_string},
        'Distance': {'req': True, 'type': FT.decimal,
                     'min': 0, 'max': 100, 'inc': 0.1},
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

    # delete record
    running_delete_query = ('DELETE FROM running WHERE date = :date')

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

    def get_all_records(self):
        query = ('SELECT * FROM running '
                 'ORDER BY "Date"')
        return self.query(query)

    def get_record(self, date):
        query = ('SELECT * FROM running '
                 'WHERE "Date" = :date')
        result = self.query(query, {"date": date})
        return result[0] if result else {}

    def add_record(self, record):
        # add record information
        insert_query = self.running_insert_query
        self.last_write = 'insert record'
        self.query(insert_query, record)

    def update_record(self, record):
        # add record information
        update_query = self.running_update_query
        self.last_write = 'update record'
        self.query(update_query, record)

    def delete_record(self, record):
        # delete record information
        delete_query = self.running_delete_query
        self.query(delete_query, record)
