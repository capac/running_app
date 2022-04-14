import sqlite3
import csv
import os
import json
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
        'Speed': {'req': True, 'type': FT.string},
        'Location': {'req': True, 'type': FT.string},
        'Period': {'req': True, 'type': FT.string_list,
                   'values': ['1', '3', '6', '9', '12']},
        }

    program_fields = {
        'Mon': {'req': True, 'type': FT.decimal},
        'Tue': {'req': True, 'type': FT.decimal},
        'Wed': {'req': True, 'type': FT.decimal},
        'Thu': {'req': True, 'type': FT.decimal},
        'Fri': {'req': True, 'type': FT.decimal},
        'Sat': {'req': True, 'type': FT.decimal},
        'Sun': {'req': True, 'type': FT.decimal},
    }

    # create tables if not existing
    create_running_table_command = ('CREATE TABLE IF NOT EXISTS running '
                                    '(Date TEXT PRIMARY KEY, '
                                    'Duration TEXT NOT NULL, '
                                    'Distance REAL NOT NULL, '
                                    'Pace TEXT NOT NULL, '
                                    'Speed TEXT NOT NULL, '
                                    'Location TEXT NOT NULL)')

    create_program_table_command = ('CREATE TABLE IF NOT EXISTS {} '
                                    '(Mon Distance REAL PRIMARY KEY, '
                                    'Tue Distance REAL, '
                                    'Wed Distance REAL, '
                                    'Thu Distance REAL, '
                                    'Fri Distance REAL, '
                                    'Sat Distance REAL, '
                                    'Sun Distance REAL)')

    # insert running session in running table
    running_insert_command = ('INSERT INTO running VALUES (:Date, '
                              ':Duration, :Distance, :Pace, :Speed, '
                              ':Location)')

    program_insert_command = ('INSERT INTO {} VALUES (:Mon, '
                              ':Tue, :Wed, :Thu, :Fri, :Sat, '
                              ':Sun)')

    # update running session in running table
    running_update_command = ('UPDATE running SET Duration=:Duration, '
                              'Distance=:Distance, '
                              'Pace=:Pace, '
                              'Speed=:Speed, '
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
    def create_db_and_primary_table(self):
        '''Creates database and table if they don't already exist'''
        self.query(self.create_running_table_command)

    # only upon first run of the running application
    def create_program_table(self, program):
        '''Creates marathon program table if it doesn't already exist'''
        self.query(self.create_program_table_command.format(program))

    def get_all_records(self):
        query = ('SELECT * FROM running ORDER BY Date DESC')
        return self.query(query)

    def get_all_program_records(self, program):
        query = ('SELECT * FROM {}'.format(program))
        return self.query(query)

    def get_record(self, date):
        query = ('SELECT * FROM running WHERE Date=:Date')
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

    def group_records_by_period(self, period):
        # group records by weekly data per year,
        # 'start_of_week' table created using suggestion below
        # https://stackoverflow.com/questions/9322313/how-to-group-by-week-no-and-get-start-date-and-end-date-for-the-week-number-in-s,
        # subsequent null entries in table converted to
        # zeros with COALESCE command in SQL.
        query = ("WITH RECURSIVE start_of_week(date_entry) AS ("
                 "VALUES((SELECT MIN(Date) FROM running)) "
                 "UNION ALL "
                 "SELECT DATE(date_entry, 'weekday 0', '+7 days') "
                 "FROM start_of_week WHERE date_entry < DATE('now')) "
                 "SELECT date_entry, "
                 "COALESCE(ROUND(Weekly_Distance, 1), 0) AS Weekly_Distance, "
                 "COALESCE(Num_Weekly_Sessions, 0) AS Num_Weekly_Sessions, "
                 "COALESCE(ROUND(Weekly_Mean_Speed, 1), 0) AS Weekly_Mean_Speed "
                 "FROM start_of_week AS sow "
                 "LEFT JOIN "
                 "(SELECT DATE(rng.Date, 'weekday 0') AS Sunday, "
                 "SUM(rng.Distance) AS Weekly_Distance, "
                 "COUNT(rng.Distance) AS Num_Weekly_Sessions, "
                 "ROUND(AVG(rng.Speed), 2) AS Weekly_Mean_Speed "
                 "FROM running AS rng "
                 "WHERE Sunday BETWEEN DATE('now', :Period) AND "
                 "DATE('now', 'weekday 0', '+7 days') "
                 "GROUP BY DATE(rng.Date, 'weekday 0')) AS rr "
                 "ON sow.date_entry = rr.Sunday "
                 "WHERE sow.date_entry BETWEEN DATE('now', :Period) AND "
                 "DATE('now', 'weekday 0', '+7 days')")
        result = self.query(query, {"Period": '-'+str(period)+' months'})
        try:
            periods, total_distances, tot_counts, mean_speed = \
                zip(*[row.values() for row in result])
        except ValueError:
            periods, total_distances, tot_counts, mean_speed = 0, 0, 0, 0
        return periods, total_distances, tot_counts, mean_speed

    def data_addition(self, data):
        '''Adds 'Pace' and 'Speed' columns and adds
        zero-padding to 'Duration' column data'''

        duration, distance = data['Duration'], data['Distance']

        # change time format from '<hh>h<mm>m<ss>s' to '<hh>:<mm>:<ss>:'
        try:
            separators = [str(duration[item]) for item in range(2, 9, 3)]
            if separators == ['h', 'm', 's']:
                data['Duration'] = f'{duration[0:2]}:{duration[3:5]}:{duration[6:8]}'
        except IndexError:
            pass
        time_in_secs = timedelta(hours=int(duration[0:2]),
                                 minutes=int(duration[3:5]),
                                 seconds=int(duration[6:8]),
                                 microseconds=0).total_seconds()
        pace_in_secs = time_in_secs/float(distance)
        minutes, seconds = divmod(pace_in_secs, 60)
        # in case rounded seconds add up to 60 add extra minute
        # and set seconds variable to zero
        if int(round(seconds, 0)) == 60:
            minutes += 1
            seconds = 0
        # zero padding added for seconds
        data['Pace'] = f'{int(minutes)}:{str(int(round(seconds, 0))).zfill(2)}'
        data['Speed'] = f'{round(3600/pace_in_secs, 1)}'
        # zero padding added for seconds
        return data


class CSVModel:
    '''CSV file retrieval and storage'''

    fields = {
        'Date': {'req': True, 'type': FT.iso_date_string},
        'Duration': {'req': True, 'type': FT.iso_time_string},
        'Distance': {'req': True, 'type': FT.decimal,
                     'min': 0, 'max': 100, 'inc': 0.1},
        'Pace': {'req': True, 'type': FT.string},
        'Speed': {'req': True, 'type': FT.string},
        'Location': {'req': True, 'type': FT.string},
        }

    program_fields = {
        'Mon': {'req': True, 'type': FT.decimal},
        'Tue': {'req': True, 'type': FT.decimal},
        'Wed': {'req': True, 'type': FT.decimal},
        'Thu': {'req': True, 'type': FT.decimal},
        'Fri': {'req': True, 'type': FT.decimal},
        'Sat': {'req': True, 'type': FT.decimal},
        'Sun': {'req': True, 'type': FT.decimal},
    }

    def __init__(self, filename, filepath=None):

        if filepath:
            if not os.path.exists(filepath):
                os.mkdir(filepath)
            self.filename = os.path.join(filepath, filename)
        else:
            self.filename = filename

    def load_records(self):
        '''Reads in all records from the CSV file and returns a list'''

        if not os.path.exists(self.filename):
            return []

        with open(self.filename, 'r', encoding='utf-8') as fh:
            # turning fh into a list is necessary for the unit tests
            csvreader = csv.DictReader(list(fh.readlines()))
            missing_fields = set(self.fields.keys()) - set(csvreader.fieldnames)
            if len(missing_fields) > 0:
                raise Exception(
                    f'''File is missing fields: {', '.join(missing_fields)}'''
                )
            else:
                return list(csvreader)

    def save_records(self, rows, keys):
        '''Save a dictionary of data to a CSV file'''

        with open(self.filename, 'w') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=keys)
            csvwriter.writeheader()
            for row in rows:
                csvwriter.writerow(row)


class SettingsModel:
    '''A model for saving settings'''

    variables = {
        # ('aqua', 'clam', 'alt', 'default', 'classic')
        'theme': {'type': 'str', 'value': 'aqua'},
        'db_name': {'type': 'str', 'value': 'running.db'},
    }

    def __init__(self, filename='settings.json', path='~'):
        # determine the file path
        self.filepath = os.path.join(os.path.expanduser(path), filename)

        # load in saved values
        self.load()

    def set(self, key, value):
        '''Set a variable value'''

        if (
            key in self.variables and type(value).__name__ == self.variables[key]['type']
        ):
            self.variables[key]['value'] = value
        else:
            raise ValueError('Bad key or wrong variable type')

    def save(self, settings=None):
        '''Save the current settings to the file'''

        json_string = json.dumps(self.variables)
        with open(self.filepath, 'w') as fh:
            fh.write(json_string)

    def load(self):
        '''Load the settings from the file'''

        # if the file doesn't exist, return
        if not os.path.exists(self.filepath):
            return
        # open the file and read the raw values
        with open(self.filepath, 'r') as fh:
            raw_values = json.loads(fh.read())
        # don't implicitly trust the raw values,
        # but only get known keys
        for key in self.variables:
            if key in raw_values and 'value' in raw_values[key]:
                raw_value = raw_values[key]['value']
                self.variables[key]['value'] = raw_value
