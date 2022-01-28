import tkinter as tk
from tkinter import ttk
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

        # database login
        self.database_login('running.db')
        if not hasattr(self, 'data_model'):
            self.destroy()
            return

        # create data model
        self.callbacks = {
            # menu bar callbacks
            # 'file->import': self.on_file_import,
            # 'file->export': self.on_file_export,
            # method callbacks
            'on_insert': self.on_insert,
            'on_remove': self.on_remove,
        }

        # data record form
        self.recordform = v.DataRecordForm(self, self.data_model.fields, self.callbacks)
        self.recordform.grid(row=2, padx=10, sticky='NSEW')
        self.recordform.columnconfigure(0, weight=1)

    def database_login(self, database):
        self.data_model = m.SQLModel(database)

    def on_insert(self):
        pass

    def on_remove(self):
        pass
