import sqlite3
from .constants import FieldTypes as FT


class SQLModel:
    '''SQL database values'''

    fields = {
        'Date': {'req': True, 'type': FT.iso_date_string},
        'Time': {'req': True, 'type': FT.iso_time_string},
        'Distance': {'req': True, 'type': FT.decimal,
                     'min': 0, 'max': 100, 'inc': 0.1},
        'Pace': {'req': True, 'type': FT.string},
        'Location': {'req': True, 'type': FT.string},
    }

    # create tables if not existing
    create_running_table_command = ('CREATE TABLE IF NOT EXISTS running '
                                    '(Date TEXT PRIMARY KEY, '
                                    'Time TEXT NOT NULL, '
                                    'Distance REAL NOT NULL, '
                                    'Pace TEXT NOT NULL, '
                                    'Location TEXT NOT NULL)')

    # insert running session in running table
    running_insert_command = ('INSERT INTO running VALUES (:Date, '
                              ':Time, :Distance, :Pace, :Location)')

    # update running session in running table
    running_update_command = ('UPDATE running SET Time=:Time, '
                              'Distance=:Distance, '
                              'Location=:Location, '
                              'WHERE Date=:Date')

    # delete record
    running_delete_command = ('DELETE FROM running WHERE Date=:Date')

    # create or connect to a database
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()
        try:
            if parameters is not None:
                cursor.execute(query, parameters)
            else:
                parameters = {}
                cursor.execute(query, parameters)
        except (sqlite3.Error) as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()
            if cursor.description is not None:
                result = [dict(row) for row in cursor.fetchall()]
                return result

    # only upon first run of the running application
    def create_db_and_tables(self):
        '''Creates database and tables if they don't already exist'''

        self.query(self.create_running_table_command)

    def get_all_records(self):
        query = ('SELECT * FROM running '
                 'ORDER BY Date')
        return self.query(query)

    def get_record(self, date):
        query = ('SELECT * FROM running '
                 'WHERE Date=:Date')
        result = self.query(query, {"Date": date})
        return result[0] if result else {}

    def add_record(self, record):
        # add record information
        insert_query = self.running_insert_command
        self.last_write = 'insert record'
        self.query(insert_query, record)

    def update_record(self, record):
        # add record information
        update_query = self.running_update_command
        self.last_write = 'update record'
        self.query(update_query, record)

    def delete_record(self, record):
        # delete record information
        delete_query = self.running_delete_command
        self.query(delete_query, record)
