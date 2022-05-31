import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from . import views as v
from . import models as m
import os


class Application(tk.Tk):
    '''Application root window'''

    # supported platforms: macOS and Windows
    config_dirs = {
        'Darwin': "~/Library/Application Support/RunningApp",
        'Windows': "~/AppData/Local/RunningApp",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # application title
        self.title('Running Application')
        self.resizable(width=False, height=False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_cordinate = int(screen_width/50)
        y_cordinate = int(screen_height/60)

        self.geometry("+{}+{}".format(x_cordinate, y_cordinate))

        # application name
        ttk.Label(self, text='Running List', font=('TkDefaultFont', 16)).grid(row=0, padx=60)

        self.inserted_rows = []
        self.updated_rows = []

        # default filename
        self.filename = tk.StringVar()

        # settings model and settings
        config_dir = self.config_dirs.get(platform.system(), '~')
        self.settings_model = m.SettingsModel(path=config_dir)
        self.load_settings()

        # database login
        self.database_login()
        if not hasattr(self, 'data_model'):
            self.destroy()
            return

        # create data model
        self.callbacks = {
            # menu bar callbacks
            'file->import': self.file_import,
            'file->export': self.file_export,
            'file->add_plan': self.add_plan,
            'on_show_plan': self.show_plan,
            'on_open_remove_plan_window': self.open_remove_plan_window,
            # method callbacks
            'on_open_record': self.open_record,
            'on_insert': self.insert,
            'on_remove': self.remove,
            'on_remove_plan': self.remove_plan,
            'on_period_dropdown': self.period_dropdown,
            'on_advanced_search': self.advanced_search,
        }

        self.menu = v.MainMenu(self, self.callbacks, self.data_model.check_program_tables())
        self.config(menu=self.menu)

        # create database and table if non-existent
        self.data_model.create_db_and_primary_table()

        # bar chart plots
        self.barcharts = v.BarChartView(self, self.data_model.group_records_by_period)
        self.barcharts.grid(row=0, column=0, sticky=('NSEW'))
        self.barcharts.columnconfigure(0, weight=1)

        # selection form
        self.selectionform = v.DataSelectionForm(self, self.data_model.running_fields,
                                                 self.callbacks)
        self.selectionform.grid(row=1, column=0, padx=4, pady=(25, 0), sticky=('NSEW'))
        self.selectionform.columnconfigure(0, weight=1)

        # treeview record form
        self.recordlist = v.RecordList(self, self.callbacks,
                                       inserted=self.inserted_rows,
                                       updated=self.updated_rows,)
        self.recordlist.grid(row=0, column=1, padx=10, sticky='NSEW')
        self.recordlist.columnconfigure(0, weight=1)
        self.populate_recordlist()

        # data record form
        self.recordform = v.DataRecordForm(self, self.data_model.running_fields, self.callbacks)
        self.recordform.grid(row=1, column=1, padx=10, sticky='NSEW')
        self.recordform.columnconfigure(0, weight=1)

        # status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(self, textvariable=self.status)
        self.statusbar.grid(row=2, column=0, padx=10, sticky=('WE'))
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
        '''Handles adding or updating new record(s) to database'''

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

        # get data and add 'Pace' and 'Speed' columns
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
            key = (str(data['Date']), str(data['Duration']),
                   str(data['Distance']), str(data['Pace']),
                   str(data['Speed']), str(data['Location']))
            # updated record
            if self.data_model.last_write == 'update record':
                self.updated_rows.append(key)
            # added record
            elif self.data_model.last_write == 'insert record':
                self.inserted_rows.append(key)
            self.populate_recordlist()
            self.period_dropdown()

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
            self.period_dropdown()

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
                records = csv_read.load_records(csv_read.running_fields)
                for row in records:
                    row = self.data_model.data_addition(row)
                    self.data_model.add_record(row)
                self.status.set(f'''Loaded running records into {self.settings['db_name'].get()}''')
                self.populate_recordlist()
                self.period_dropdown()

    def file_export(self):
        '''Handles the file->export action from the menu'''

        filename = filedialog.asksaveasfilename(
            title='Select the target file for saving records',
            defaultextension='.csv',
            filetypes=[('Comma-Separated Values', '*.csv *.CSV')]
        )
        if filename:
            self.filename.set(filename)
            try:
                rows = self.data_model.get_all_records()
            except Exception as e:
                messagebox.showerror(
                    title='Error',
                    message='Problem reading database',
                    detail=str(e)
                )
            else:
                self.status.set(f'Saved data to {self.filename.get()}')
                csv_write = m.CSVModel(filename=self.filename.get(),
                                       filepath=None)
                csv_write.save_records(rows, csv_write.running_fields.keys())

    def period_dropdown(self):
        period = self.selectionform.get()
        self.barcharts = v.BarChartView(self, self.data_model.group_records_by_period,
                                        period)
        self.barcharts.grid(row=0, column=0, sticky=(tk.W + tk.E))

    def add_plan(self):
        '''Handles marathon program import and saves data to the database,
        creates a menu bar entry to view marathon program bar chart'''

        filename = filedialog.askopenfilename(
            title='Select the file to import into the database',
            defaultextension='.csv',
            filetypes=[('Comma-Separated Values', '*.csv *.CSV')]
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
                basename, _ = os.path.splitext(os.path.basename(self.filename.get()))
                try:
                    self.data_model.create_program_table(basename)
                except Exception as e:
                    messagebox.showerror(
                        title='Error',
                        message='Problem adding data to database',
                        detail=str(e)
                    )
                else:
                    records = csv_read.load_records(csv_read.program_fields)
                    for row in records:
                        self.data_model.add_program_record(basename, row)
                    messagebox.showinfo(
                            title='Adding program',
                            message=f'Added {basename} program.\n\nPress button to continue.',
                        )
                    self.status.set(f'''Loaded {basename} records into {self.settings['db_name'].get()}''')
                    self.menu.add_program_menu(basename)

    def show_plan(self, table_name):
        '''opens new window for marathon program stacked bar chart'''

        plan_window = tk.Toplevel()
        plan_window.resizable(width=False, height=False)
        plan_window.title('Marathon program')

        # get marathon plan data
        try:
            days_of_week, weekly_distances = self.data_model.get_all_program_records(table_name)
            stackedbarchart = v.StackedBarChartView(plan_window, table_name,
                                                    days_of_week, weekly_distances)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem reading database',
                detail=str(e)
            )
        else:
            stackedbarchart.grid(row=0, padx=5, pady=5, sticky='NSEW')
            stackedbarchart.columnconfigure(0, weight=1)

    def open_remove_plan_window(self):
        '''opens new window for marathon program removal'''

        self.removal_window = tk.Toplevel()
        self.removal_window.resizable(width=False, height=False)
        self.removal_window.title('Marathon program')

        # retrieval marathon program tables
        try:
            updated_tables = self.data_model.check_program_tables()
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem reading database',
                detail=str(e)
            )

        # property form
        self.deletetableform = v.DeleteTableForm(self.removal_window,
                                                 self.data_model.program_fields,
                                                 self.callbacks, updated_tables)
        self.deletetableform.grid(row=0, padx=5, sticky='W')
        self.deletetableform.columnconfigure(0, weight=1)

    def remove_plan(self):
        '''Removes property from database'''

        # get table
        table = self.deletetableform.get()
        try:
            self.data_model.remove_program_table(table)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem deleting table',
                detail=str(e)
            )
        else:
            self.records_deleted += 1
            self.menu.remove_menu(table)
            self.removal_window.destroy()
            messagebox.showinfo(
                title='Removing program',
                message=f'Removed {table} program.\n\nPress button to continue.',
                )
            self.status.set(f'{self.records_deleted} table(s) deleted this session')

    def advanced_search(self):
        '''Advanced search window'''

        advanced_window = tk.Toplevel()
        advanced_window.resizable(width=False, height=False)
        advanced_window.title('Advanced search')

    def load_settings(self):
        '''Load settings into our self.settings dict'''

        vartypes = {
            'bool': tk.BooleanVar,
            'str': tk.StringVar,
            'int': tk.IntVar,
            'float': tk.DoubleVar
        }

        # create our dict of settings variables from the model's settings
        self.settings = {}
        for key, data in self.settings_model.variables.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])

        # put a trace on the variables so they get stored when changed
        for var in self.settings.values():
            var.trace('w', self.save_settings)

    def save_settings(self, *args):
        '''Save the current settings to a preferences file'''

        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
        self.settings_model.save()

    def database_login(self):
        db_name = self.settings['db_name'].get()
        self.data_model = m.SQLModel(db_name)
