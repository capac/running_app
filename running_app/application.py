import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from . import views as v
from . import models as m
from . import network as n
import os
from datetime import timedelta


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
        ttk.Label(self, text='', font=('TkDefaultFont', 16),
                  foreground='black',).grid(row=0, padx=60, pady=2)

        self.inserted_rows = []
        self.updated_rows = []

        # default filename
        self.filename = tk.StringVar()

        # settings model and settings
        config_dir = self.config_dirs.get(platform.system(), '~')
        self.settings_model = m.SettingsModel(path=config_dir)
        self.load_settings()

        style = ttk.Style()
        theme = self.settings.get('theme').get()
        # Themes: 'aqua', 'clam', 'alt', 'default', 'classic'; 'aqua' set as default
        if theme in style.theme_names():
            style.theme_use(theme)

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
            'on_open_search_window': self.open_search_window,
            'on_search': self.search,
        }

        self.menu = v.MainMenu(self, self.callbacks,
                               self.data_model.check_program_tables())
        self.config(menu=self.menu)

        # create database and table if non-existent
        self.data_model.create_db_and_primary_table()

        # bar chart plots
        self.barcharts = v.BarChartView(self, self.data_model.group_records_by_period)
        self.barcharts.grid(row=1, column=0, sticky=('NSEW'))
        self.barcharts.columnconfigure(0, weight=1)

        # treeview record form
        self.recordlist = v.RecordList(self, self.callbacks,
                                       inserted=self.inserted_rows,
                                       updated=self.updated_rows,)
        self.recordlist.grid(row=1, column=1, padx=10, sticky='NSEW')
        self.recordlist.columnconfigure(0, weight=1)
        self.populate_recordlist()

        # interaction form
        self.selectionform = v.DataInteractionForm(self,
                                                   self.data_model.running_fields,
                                                   self.callbacks,
                                                   n.get_local_weather(self.settings
                                                                       ['post_code'].get(),
                                                                       self.settings
                                                                       ['country_code'].get()))
        self.selectionform.grid(row=2, column=0, padx=4, pady=(25, 0), sticky=('NSEW'))
        self.selectionform.columnconfigure(0, weight=1)

        # data record form
        self.recordform = v.DataRecordForm(self, self.data_model.running_fields,
                                           self.callbacks)
        self.recordform.grid(row=2, column=1, padx=10, sticky='NSEW')
        self.recordform.columnconfigure(0, weight=1)

        # status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(self, textvariable=self.status, foreground='black')
        self.statusbar.grid(row=3, column=0, padx=10, sticky=('WE'))
        self.statusbar.columnconfigure(0, weight=1)

        self.records_saved = 0
        self.records_updated = 0
        self.records_deleted = 0

    def populate_recordlist(self):
        '''refresh treeview with records'''

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
                self.recordform.tkraise()
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
            detail = 'The following fields have errors: \n * {}'\
                     .format('\n * '.join(errors.keys()))
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
                try:
                    records = csv_read.load_records(csv_read.running_fields)
                    for row in records:
                        row = self.data_model.data_addition(row)
                        self.data_model.add_record(row)
                    self.status.set(f'Loaded running records '
                                    f'''into {self.settings['db_name'].get()}''')
                    self.populate_recordlist()
                    self.period_dropdown()
                except TypeError:
                    messagebox.showerror(
                        title='Error',
                        message='Cannot add data to table',
                    )

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
        period = self.selectionform.periodvalue.get()
        self.barcharts = v.BarChartView(self, self.data_model.group_records_by_period,
                                        period)
        self.barcharts.grid(row=1, column=0, sticky=(tk.W + tk.E))

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
                        message='Problem creating table in database',
                        detail=str(e)
                    )
                else:
                    try:
                        records = csv_read.load_records(csv_read.program_fields)
                        for row in records:
                            self.data_model.add_program_record(basename, row)
                        messagebox.showinfo(
                                title='Adding program',
                                message=f'Added {basename} program.\n'
                                        f'Press button to continue.',
                            )
                        self.status.set(f'Loaded {basename} records into '
                                        f'''{self.settings['db_name'].get()}''')
                        self.menu.add_program_menu(basename)
                    except TypeError:
                        messagebox.showerror(
                            title='Error',
                            message='Cannot add data to table',
                        )
                        self.data_model.remove_program_table(basename)

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
                message=f'Removed {table} program.\n'
                        f'Press button to continue.',
                )
            self.status.set(f'{self.records_deleted} table(s) deleted this session')

    def open_search_window(self):
        '''Advanced search window'''

        advanced_window = tk.Toplevel(self)
        advanced_window.resizable(width=False, height=False)
        advanced_window.title('Advanced search')

        # advanced selection form
        min_date = self.data_model.min_max_column_values()[0]
        max_date = self.data_model.min_max_column_values()[1]
        valid_dates = self.data_model.get_dates(min_date, max_date)
        self.advancedsearch = v.SearchForm(advanced_window, self.data_model.running_fields,
                                           self.callbacks, valid_dates=valid_dates)
        self.advancedsearch.grid(row=0, column=0, padx=6, pady=6, sticky='NSEW')
        self.advancedsearch.columnconfigure(0, weight=1)

        # treeview record form
        self.search_recordlist = v.RecordList(advanced_window, self.callbacks,
                                              inserted=self.inserted_rows,
                                              updated=self.updated_rows,)
        self.search_recordlist.grid(row=1, column=0, padx=10, sticky='NSEW')
        self.search_recordlist.columnconfigure(0, weight=1)

        # search status bar
        self.search_status = tk.StringVar()
        self.search_statusbar = ttk.Label(advanced_window,
                                          textvariable=self.search_status,
                                          foreground='black')
        self.search_statusbar.grid(row=2, column=0, padx=10, sticky=('WE'))
        self.search_statusbar.columnconfigure(0, weight=1)

    def search(self):

        # check for errors first
        errors = self.advancedsearch.get_errors()
        if errors:
            message = 'Cannot search for record(s)'
            detail = 'The following fields have errors: \n * {}'\
                     .format('\n * '.join(errors.keys()))
            self.search_status.set('Cannot search for record(s)')
            messagebox.showerror(title='Error', message=message, detail=detail)
            return False
        try:
            search_inputs = self.advancedsearch.get()
            search_outputs = self.data_model.get_record_range(**search_inputs)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem searching for record(s)',
                detail=str(e)
            )
            self.search_status.set('Problem searching for record(s)')
        else:
            self.search_recordlist.populate(search_outputs)
            self.search_status.set('Count: {} | Distance: {} km | Mean speed: {} km/hr | Duration: {} hr'
                                   .format(*self._stats_summary(search_outputs)))

    def _stats_summary(self, search_outputs):
        count, tot_dist, sum_speed, tot_time, mean_speed = 0, 0, 0, 0, 0
        for row in search_outputs:
            count += 1
            tot_dist += row['Distance']
            sum_speed += row['Speed']
            tot_time += timedelta(hours=int(row['Duration'][0:2]),
                                  minutes=int(row['Duration'][3:5]),
                                  seconds=int(row['Duration'][6:8]),
                                  microseconds=0).total_seconds()
        tot_dist = str(round(tot_dist, 2))
        try:
            mean_speed = str(round(sum_speed/len(search_outputs), 2))
        except ZeroDivisionError:
            messagebox.showerror(
                title='Error',
                message='No record(s) in search',
            )
        tot_time = str(timedelta(seconds=tot_time))
        return count, tot_dist, mean_speed, tot_time

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
