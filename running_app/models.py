import sqlite3
from datetime import timedelta
from .constants import FieldTypes as FT


class SQLModel:
    '''SQL database values'''

    fields = {
        'Date': {'req': True, 'type': FT.iso_date_string},
        'Duration': {'req': True, 'type': FT.iso_time_string},
        'Distance': {'req': True, 'type': FT.decimal,
                     'min': 0, 'max': 100, 'inc': 0.1},
        'Pace': {'req': True, 'type': FT.string},
        'Location': {'req': True, 'type': FT.string},
    }

    # create tables if not existing
    create_running_table_command = ('CREATE TABLE IF NOT EXISTS running '
                                    '(Date TEXT PRIMARY KEY, '
                                    'Duration TEXT NOT NULL, '
                                    'Distance REAL NOT NULL, '
                                    'Pace TEXT NOT NULL, '
                                    'Location TEXT NOT NULL)')

    # insert running session in running table
    running_insert_command = ('INSERT INTO running VALUES (:Date, '
                              ':Duration, :Distance, :Pace, :Location)')

    # update running session in running table
    running_update_command = ('UPDATE running SET Duration=:Duration, '
                              'Distance=:Distance, '
                              'Pace=:Pace, '
                              'Location=:Location '
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
        query_date = record['Date']
        results = self.get_record(query_date)
        # if no previous record exists then add it
        if not results:
            query = self.running_insert_command
            self.last_write = 'insert record'
        # if the record exists then update it
        else:
            query = self.running_update_command
            self.last_write = 'update record'
        self.query(query, record)

    def delete_record(self, record):
        # delete record information
        delete_query = self.running_delete_command
        self.query(delete_query, record)

    def data_addition(self, data):
        '''Adds 'Pace' column and adds zero-padding to 'Duration' column data'''

        duration, distance = data['Duration'], data['Distance']
        time_in_secs = timedelta(hours=int(duration[0:2]),
                                 minutes=int(duration[3:5]),
                                 seconds=int(duration[6:8]),
                                 microseconds=0).total_seconds()
        minutes, seconds = divmod(time_in_secs/float(distance), 60)
        data['Pace'] = f'{int(minutes)}:{str(int(round(seconds, 0))).zfill(2)}'
        # zero padding for seconds column
        data['Duration'] = ':'.join(x.zfill(2) for x in data['Duration'].split(':'))
        return data
