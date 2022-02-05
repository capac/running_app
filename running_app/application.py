import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from . import views as v
from . import models as m


class Application(tk.Tk):
    '''Application root window'''

    # supported platforms: macOS and Windows
    config_dirs = {
        'Darwin': "~/Library/Application Support/RunningApp",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # application title
        self.title('Running Application')
        self.resizable(width=False, height=False)

        # application name
        ttk.Label(self, text='Running List', font=('TkDefaultFont', 16)).grid(row=0, padx=60)

        self.inserted_rows = []
        self.updated_rows = []

        # database login
        self.database_login('running.db')
        if not hasattr(self, 'data_model'):
            self.destroy()
            return

        # create data model
        self.callbacks = {
            # menu bar callbacks
            'file->import': self.file_import,
            'file->export': self.file_export,
            'on_show_running_progression': self.show_running_progression,
            'on_show_vo2max': self.show_vo2max,
            # method callbacks
            'on_open_record': self.open_record,
            'on_insert': self.insert,
            'on_remove': self.remove,
        }

        menu = v.MainMenu(self, self.callbacks)
        self.config(menu=menu)

        # create database and tables if non-existent
        self.data_model.create_db_and_tables()

        # treeview record form
        self.recordlist = v.RecordList(self, self.callbacks,
                                       inserted=self.inserted_rows,
                                       updated=self.updated_rows,)
        self.recordlist.grid(row=1, padx=10, sticky='NSEW')
        self.recordlist.columnconfigure(0, weight=1)
        self.populate_recordlist()

        # data record form
        self.recordform = v.DataRecordForm(self, self.data_model.fields, self.callbacks)
        self.recordform.grid(row=2, padx=10, sticky='NSEW')
        self.recordform.columnconfigure(0, weight=1)

        # refresh screen to update recordlist / recordform, solution found below:
        # https://stackoverflow.com/questions/44768319/tkinter-label-not-appearing
        self.update()

        # status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(self, textvariable=self.status)
        self.statusbar.grid(row=3, padx=10, sticky=('WE'))
        self.statusbar.columnconfigure(0, weight=1)

        self.records_saved = 0
        self.records_updated = 0
        self.records_deleted = 0

    def populate_recordlist(self):
        try:
            rows = self.data_model.get_all_records()
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem reading database',
                detail=str(e)
            )
        else:
            self.recordlist.populate(rows)

    def open_record(self, rowkey=None):
        '''rowkey is simply date, while data contains the information for the date'''

        if rowkey is None:
            data = None
        else:
            try:
                data = self.data_model.get_record(rowkey)
                self.recordform.load_record(rowkey, data)
                self.recordform.tkraise(aboveThis=self.recordlist)
            except Exception as e:
                messagebox.showerror(title='Error', message='Problem reading database',
                                     detail=str(e))
                return

    def insert(self):
        '''Handles adding new record(s) to database'''

        # check for errors first
        errors = self.recordform.get_errors()
        if errors:
            message = 'Cannot save record'
            detail = 'The following fields have errors: \n * {}'.format('\n * '.join(errors.keys()))
            self.status.set(
                f'''Cannot save, error in fields: {', '.join(errors.keys())}'''
            )
            messagebox.showerror(title='Error', message=message, detail=detail)
            return False

        # get data and add 'Pace' column
        data = self.data_model.data_addition(self.recordform.get())
        try:
            self.data_model.add_record(data)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem saving record',
                detail=str(e)
            )
            self.status.set('Problem saving record')
        else:
            self.records_updated += 1
            self.status.set(f'{self.records_updated} record(s) updated this session')
            key = (data['Date'], data['Duration'], data['Distance'], data['Location'])
            # updated record
            if self.data_model.last_write == 'update record':
                self.updated_rows.append(key)
            # added record
            elif self.data_model.last_write == 'insert record':
                self.inserted_rows.append(key)
            self.populate_recordlist()

    def remove(self):
        '''Removes record from database'''

        # get data
        data = self.recordform.get()
        try:
            self.data_model.delete_record(data)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem deleting record',
                detail=str(e)
            )
            self.status.set('Problem deleting record')
        else:
            self.records_deleted += 1
            self.status.set(f'{self.records_deleted} record(s) deleted this session')
            self.recordform.reset()
            self.populate_recordlist()

    # import records from CSV file to database
    def file_import(self):
        '''Handles the file->import action from the menu'''

        filename = filedialog.askopenfilename(
            title='Select the file to import into the database',
            defaultextension='.csv',
            filetypes=[('Comma-Separated Values', '*.csv, *.CSV')]
        )
        if filename:
            self.filename.set(filename)
            try:
                csv_read = m.CSVModel(filename=self.filename.get(),
                                      filepath=None)
            except Exception as e:
                messagebox.showerror(
                    title='Error',
                    message='Problem reading file',
                    detail=str(e)
                )
            else:
                records = csv_read.load_records()
                for row in records:
                    self.data_model.add_record(row)
                self.status.set(f'''Loaded data into {self.settings['db_name'].get()}''')
                self.populate_recordlist()

    def file_export(self):
        pass

    def show_running_progression(self):
        pass

    def show_vo2max(self):
        pass

    def database_login(self, database):
        self.data_model = m.SQLModel(database)
