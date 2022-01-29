import tkinter as tk
from tkinter import ttk, messagebox
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
            'on_insert': self.insert,
            'on_update': self.update,
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
        self.main_status = tk.StringVar()
        self.main_statusbar = ttk.Label(self, textvariable=self.main_status)
        self.main_statusbar.grid(row=3, padx=10, sticky=('WE'))
        self.main_statusbar.columnconfigure(0, weight=1)

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
        '''rowkey is simply row_id, while data contains the information for the row_id'''

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
        '''Handles tenant updates to database'''

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

        # get data
        data = self.recordform.get()
        try:
            self.data_model.add_record(data)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem saving record',
                detail=str(e)
            )
            self.main_status.set('Problem saving record')
        else:
            self.records_updated += 1
            self.main_status.set(f'{self.records_updated} record(s) updated this session')
            key = (data['Date'], data['Time'], data['Distance'], data['Location'])
            # old property with updated tenant
            if self.data_model.last_write == 'update record':
                self.updated_rows.append(key)
            # new property with added tenant
            elif self.data_model.last_write == 'insert record':
                self.inserted_rows.append(key)
            self.populate_recordlist()

    def update(self):
        pass

    def remove(self):
        pass

    def file_import(self):
        pass

    def file_export(self):
        pass

    def show_running_progression(self):
        pass

    def show_vo2max(self):
        pass

    def database_login(self, database):
        self.data_model = m.SQLModel(database)
