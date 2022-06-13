import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from . import widgets as w
from re import split


class MainMenu(tk.Menu):
    '''The Application's main menu'''

    def __init__(self, parent, callbacks, table_checks, *args, **kwargs):
        '''Constructor for MainMenu

        arguments:
            parent - the parent widget
            callbacks - a dict containing Python callbacks
            settings - dict to save user settings
        '''
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks
        self.table_checks = table_checks
        self.menu_count = tk.IntVar()

        # the file menu
        self.file_menu = tk.Menu(self, tearoff=False)
        self.file_menu.add_command(
                 # 8230: ASCII value for horizontal ellipsis
                 label='Import file with running data'+chr(8230),
                 command=self.callbacks['file->import']
                 )
        self.file_menu.add_command(
                 # 8230: ASCII value for horizontal ellipsis
                 label='Export file with running data'+chr(8230),
                 command=self.callbacks['file->export']
                 )
        self.file_menu.add_separator()
        self.file_menu.add_command(
                 # 8230: ASCII value for horizontal ellipsis
                 label='Add marathon plan'+chr(8230),
                 command=self.callbacks['file->add_plan']
                 )
        self.menu_count.set(0)
        if self.table_checks:
            for table in self.table_checks:
                self.add_program_menu(table)
        self.add_cascade(label='File', menu=self.file_menu)

        # the help menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='About'+chr(8230), command=self.show_about)
        self.add_cascade(label='Help', menu=help_menu)

    # add marathon program to drop down menu when importing program
    def add_program_menu(self, table_name):
        self.menu_count.set(self.menu_count.get()+1)
        if self.menu_count.get() == 1:
            self.add_remove_program_entry()
        self.file_menu.add_command(
                # 8230: ASCII value for horizontal ellipsis
                label="Show "+table_name+" marathon plan"+chr(8230),
                command=lambda: self.callbacks['on_show_plan'](table_name),
                )
        self.file_menu.update()

    # just adds 'Remove marathon plan' label
    def add_remove_program_entry(self):
        self.file_menu.add_command(
            # 8230: ASCII value for horizontal ellipsis
            label='Remove marathon plan'+chr(8230),
            command=self.callbacks['on_open_remove_plan_window']
            )

    # removes marathon plan entry from file menu
    def remove_menu(self, table_name):
        self.file_menu.delete("Show "+table_name+" marathon plan"+chr(8230))
        self.menu_count.set(self.menu_count.get()-1)
        if self.menu_count.get() == 0:
            self.file_menu.delete("Remove marathon plan"+chr(8230))
        self.file_menu.update()

    def show_about(self):
        '''Show the about dialog'''
        about_message = 'Running Application'
        about_details = ('Running record application \
                         for the query of information \
                         concerning training progression and personal bests.\n\n\
                         For assistance please contact the author.')
        messagebox.showinfo(title='About', message=about_message, detail=about_details)


class DataRecordForm(tk.Frame):
    '''The record form for our widgets'''

    def __init__(self, parent, fields, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks

        # a dictionary to keep track of input widgets
        self.inputs = {}

        # build the form
        self.record_label = ttk.Label(self)
        self.record_label.grid(row=0, column=0, padx=2, pady=(4, 0))

        # running input
        runninginfo = tk.LabelFrame(self, text='Running information', padx=5, pady=5)

        self.inputs['Date'] = w.LabelInput(runninginfo, 'Date (YYYY-mm-dd)',
                                           field_spec=fields['Date'],
                                           input_args={'width': 12},
                                           label_args={'width': 18})
        self.inputs['Date'].grid(row=0, column=0)
        self.inputs['Duration'] = w.LabelInput(runninginfo, 'Duration (hh:mm:ss)',
                                               field_spec=fields['Duration'],
                                               input_args={'width': 12},
                                               label_args={'width': 18})
        self.inputs['Duration'].grid(row=0, column=1)
        self.inputs['Distance'] = w.LabelInput(runninginfo, 'Distance (km)',
                                               field_spec=fields['Distance'],
                                               input_args={'width': 12},
                                               label_args={'width': 18})
        self.inputs['Distance'].grid(row=0, column=2)
        self.inputs['Location'] = w.LabelInput(runninginfo, 'Location (City, Country)',
                                               field_spec=fields['Location'],
                                               input_args={'width': 12},
                                               label_args={'width': 18})
        self.inputs['Location'].grid(row=0, column=3)
        runninginfo.grid(row=1, column=0, sticky=(tk.W + tk.E))

        # command section
        command_section = tk.LabelFrame(self, text='Commands', padx=5, pady=5)
        self.insertbutton = w.LabelInput(command_section, 'Add / update data',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_insert'])
        self.insertbutton.grid(row=0, column=0, padx=8, pady=(10, 0))
        self.removebutton = w.LabelInput(command_section, 'Remove data',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_remove'])
        self.removebutton.grid(row=0, column=1, padx=8, pady=(10, 0))
        self.searchbutton = w.LabelInput(command_section, 'Search',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_open_search_window'])
        self.searchbutton.grid(row=0, column=2, padx=(200, 0), pady=(10, 0))
        command_section.grid(row=2, column=0, sticky=(tk.W + tk.E))

    def get(self):
        '''Retrieve data from Tkinter and place it in regular Python objects'''

        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data

    def get_errors(self):
        '''Get a list of field errors in the form'''

        errors = {}
        for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()
        return errors

    def reset(self):
        '''Resets the form entries'''

        # clear all values
        for widget in self.inputs.values():
            widget.set('')

    def load_record(self, rowkey, data=None):
        self.record_label.config(text='Date: {}'.format(rowkey))
        for key, widget in self.inputs.items():
            self.inputs[key].set(data.get(key, ''))
            try:
                widget.input.trigger_focusout_validation()
            except AttributeError:
                pass


class DataSelectionForm(tk.Frame):
    '''The selection form for our bar chart'''

    def __init__(self, parent, fields, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks

        # selection dropdown
        selectioninfo = tk.LabelFrame(self, text='Selection information', padx=5, pady=5)
        self.selectionvalue = w.LabelInput(selectioninfo, 'Select period',
                                           field_spec=fields['Period'])
        self.selectionvalue.set(fields['Period']['values'][0])
        self.selectionvalue.grid(row=0, column=0)
        self.selectbutton = w.LabelInput(selectioninfo, 'Select',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_period_dropdown'])
        self.selectbutton.grid(row=0, column=1, padx=5, pady=(18, 0))
        selectioninfo.grid(row=0, column=0, sticky=(tk.W + tk.E))

    def get(self):
        return self.selectionvalue.get()


class SearchForm(tk.Frame):
    '''Selection form for advanced search, shows output in treeview'''

    def __init__(self, parent, fields, callbacks, valid_dates, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks

        # a dictionary to keep track of input widgets
        self.search_inputs = {}

        # advanced selection form
        advancedselectioninfo = tk.LabelFrame(self, text='Advanced selection', padx=5, pady=5)
        self.search_inputs['date_lo'] = w.LabelInput(advancedselectioninfo, 'Date: lower',
                                                     input_class=ttk.Combobox,
                                                     input_args={'width': 11,
                                                                 'values': valid_dates},)
        self.search_inputs['date_lo'].grid(row=0, column=0, padx=8, pady=(20, 0),
                                           sticky=(tk.W + tk.E))
        self.search_inputs['date_hi'] = w.LabelInput(advancedselectioninfo, 'Date: upper',
                                                     input_class=ttk.Combobox,
                                                     input_args={'width': 11,
                                                                 'values': valid_dates},)
        self.search_inputs['date_hi'].grid(row=1, column=0, padx=8, sticky=(tk.W + tk.E))
        self.search_inputs['duration_lo'] = w.LabelInput(advancedselectioninfo,
                                                         'Duration: lower',
                                                         input_class=ttk.Entry,
                                                         input_args={'width': 9},)
        self.search_inputs['duration_lo'].grid(row=0, column=1, padx=8, pady=(20, 0),
                                               sticky=(tk.W + tk.E))
        self.search_inputs['duration_hi'] = w.LabelInput(advancedselectioninfo,
                                                         'Duration: upper',
                                                         input_class=ttk.Entry,
                                                         input_args={'width': 9},)
        self.search_inputs['duration_hi'].grid(row=1, column=1, padx=8,
                                               sticky=(tk.W + tk.E))
        self.search_inputs['distance_lo'] = w.LabelInput(advancedselectioninfo,
                                                         'Distance: lower',
                                                         field_spec=fields['Distance'],
                                                         input_args={'width': 6},)
        self.search_inputs['distance_lo'].grid(row=0, column=2, padx=8, pady=(20, 0),
                                               sticky=(tk.W + tk.E))
        self.search_inputs['distance_hi'] = w.LabelInput(advancedselectioninfo,
                                                         'Distance: upper',
                                                         field_spec=fields['Distance'],
                                                         input_args={'width': 6},)
        self.search_inputs['distance_hi'].grid(row=1, column=2, padx=8, sticky=(tk.W + tk.E))
        self.search_inputs['pace_lo'] = w.LabelInput(advancedselectioninfo, 'Pace: lower',
                                                     input_class=ttk.Entry,
                                                     input_args={'width': 6},)
        self.search_inputs['pace_lo'].grid(row=0, column=3, padx=8, pady=(20, 0),
                                           sticky=(tk.W + tk.E))
        self.search_inputs['pace_hi'] = w.LabelInput(advancedselectioninfo,
                                                     'Pace: upper',
                                                     input_class=ttk.Entry,
                                                     input_args={'width': 6},)
        self.search_inputs['pace_hi'].grid(row=1, column=3, padx=8, sticky=(tk.W + tk.E))
        self.search_inputs['speed_lo'] = w.LabelInput(advancedselectioninfo,
                                                      'Speed: lower',
                                                      field_spec=fields['Distance'],
                                                      input_args={'width': 6},)
        self.search_inputs['speed_lo'].grid(row=0, column=4, padx=8, pady=(20, 0),
                                            sticky=(tk.W + tk.E))
        self.search_inputs['speed_hi'] = w.LabelInput(advancedselectioninfo,
                                                      'Speed: upper',
                                                      field_spec=fields['Distance'],
                                                      input_args={'width': 6},)
        self.search_inputs['speed_hi'].grid(row=1, column=4, padx=8, sticky=(tk.W + tk.E))
        self.search_button = w.LabelInput(advancedselectioninfo, 'Search',
                                          input_class=ttk.Button,
                                          input_var=self.callbacks['on_search'])
        self.search_button.grid(row=1, column=5, padx=8, pady=(20, 5))
        advancedselectioninfo.grid(row=0, column=0, sticky='EW')

    def get(self):
        '''Retrieve data from Tkinter and place it in regular Python objects'''

        search_data = {}
        for key, widget in self.search_inputs.items():
            search_data[key] = widget.get()
        return search_data

    def get_errors(self):
        '''Get a list of field errors in the form'''

        search_errors = {}
        for key, widget in self.search_inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                search_errors[key] = widget.error.get()
        return search_errors


class RecordList(tk.Frame):
    '''Display records in the database'''

    column_defs = {
        '#0': {'label': 'Row', 'anchor': tk.W},
        'Date': {'label': 'Date (YYYY-mm-dd)', 'width': 120},
        'Duration': {'label': 'Duration (hh:mm:ss)', 'width': 120},
        'Distance': {'label': 'Distance (km)'},
        'Pace': {'label': 'Pace (min/km)'},
        'Speed': {'label': 'Speed (km/hr)'},
        'Location': {'label': 'Location (City, Country)', 'width': 154},
    }
    default_width = 90
    default_minwidth = 20
    default_anchor = tk.W

    def __init__(self, parent, callbacks,
                 inserted, updated,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks
        self.inserted = inserted
        self.updated = updated
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # create treeview
        self.treeview = ttk.Treeview(self, columns=list(self.column_defs.keys())[1:],
                                     selectmode='browse')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.treeview.grid(row=0, column=0, sticky='NSEW')

        # hide first column
        self.treeview.config(show='headings')

        # configure scrollbar for the treeview
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                       command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.grid(row=0, column=0, sticky='NSEW')
        self.scrollbar.grid(row=0, column=1, sticky='NSEW')

        # configure treeview columns
        for name, definition in self.column_defs.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)
            self.treeview.heading(name, text=label, anchor=anchor)
            self.treeview.column(name, anchor=anchor, minwidth=minwidth,
                                 width=width, stretch=stretch)

        # configure row tags
        self.treeview.tag_configure('inserted_record', background='lightgreen')
        self.treeview.tag_configure('updated_record', background='deepskyblue')

        # bind on row selection
        self.treeview.bind('<<TreeviewSelect>>', self.on_open_record)

    def on_open_record(self, *args):
        try:
            selected_id = self.treeview.selection()[0]
            self.callbacks['on_open_record'](selected_id.split('|')[0])
        # quick fix when window loses focus and no line is selected,
        # a better fix is to find a way to keep the line selected
        except IndexError:
            pass

        # bind on header selection
        self.reverse_sort = tk.BooleanVar()
        self.reverse_sort.set(False)
        self.treeview.bind('<Button-1>', self.on_sort_records)

    def on_sort_records(self, event):
        '''Sorts treeview list by column header name.
        See https://stackoverflow.com/questions/22032152/python-ttk-treeview-sort-numbers'''

        region = self.treeview.identify_region(event.x, event.y)
        column = self.treeview.identify_column(event.x)
        if region == 'heading':
            itemlist = list((self.treeview.set(x, column), x) for x in
                            self.treeview.get_children(''))
            if column in ('#3', '#5'):
                itemlist.sort(key=lambda x: float(x[0]), reverse=self.reverse_sort.get())
            else:
                itemlist.sort(key=lambda x: x, reverse=self.reverse_sort.get())
            for index, (_, iid) in enumerate(itemlist):
                self.treeview.move(iid, self.treeview.parent(iid), index)
        # https://stackoverflow.com/questions/17168046/python-how-to-negate-value-if-true-return-false-if-false-return-true
        self.reverse_sort.set(not (False | self.reverse_sort.get()))

    def populate(self, rows):
        '''Clear the treeview and write the supplied data rows to it'''

        for row in self.treeview.get_children():
            self.treeview.delete(row)

        valuekeys = list(self.column_defs.keys())[1:]
        for rowdata in rows:
            rowkey = (str(rowdata['Date']), str(rowdata['Duration']),
                      str(rowdata['Distance']), str(rowdata['Pace']),
                      str(rowdata['Speed']), str(rowdata['Location']))
            values = [rowdata[key] for key in valuekeys]
            if self.inserted and rowkey in self.inserted:
                tag = 'inserted_record'
            elif self.updated and rowkey in self.updated:
                tag = 'updated_record'
            else:
                tag = ''
            stringkey = '{}|{}|{}|{}|{}|{}'.format(*rowkey)
            self.treeview.insert('', 'end', iid=stringkey, text=stringkey,
                                 values=values, tag=tag)

        # selects automatically the first row, to make selections keyboard-friendly
        if len(rows) > 0:
            firstrow = self.treeview.identify_row(0)
            self.treeview.focus_set()
            self.treeview.selection_set(firstrow)
            self.treeview.focus(firstrow)


class DeleteTableForm(tk.Frame):
    '''Widget input form for deleting marathon program'''

    def __init__(self, parent, fields, callbacks, updated_table_names, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks

        # marathon program information
        tableinfo = tk.LabelFrame(self, text='Marathon program information', padx=5, pady=5)

        # line 1
        self.tablevalue = w.LabelInput(tableinfo, 'Program plans',
                                       field_spec=fields['Program dropdown'],
                                       input_args={'values': updated_table_names})
        self.tablevalue.set(updated_table_names[0])
        self.tablevalue.grid(row=0, column=0)
        self.deletebutton = w.LabelInput(tableinfo, 'Delete plan',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_remove_plan'])
        self.deletebutton.grid(row=0, column=1, padx=8, pady=(16, 0))
        tableinfo.grid(row=0, column=0, sticky=tk.W)
        tableinfo.columnconfigure(0, weight=1)

    def get(self):
        '''Retrieve data from Tkinter and place it in regular Python objects'''
        return self.tablevalue.get()


class BarChartView(tk.Frame):
    def __init__(self, parent, fields, selection=1, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.fields = fields

        # bar chart plots
        plotinfo = tk.LabelFrame(self, text='Bar charts', padx=5, pady=5)
        distance_chart = w.BarChartWidget(self, "Weeks", "Distance (km)",
                                          "Distance per week")
        distance_chart.grid(row=0, column=0, sticky=(tk.W + tk.E))
        speed_chart = w.BarChartWidget(self, "Weeks", "Mean speed (km/h)",
                                       "Weekly mean speed")
        speed_chart.grid(row=1, column=0, sticky=(tk.W + tk.E))
        count_chart = w.BarChartWidget(self, "Weeks", "Number of sessions",
                                       "Number of sessions per week")
        count_chart.grid(row=2, column=0, sticky=(tk.W + tk.E))

        periods, distances, counts, average_speed = self.fields(period=selection)
        distance_chart.draw_bar_chart(periods, distances, selection, 'dodgerblue')
        speed_chart.draw_bar_chart(periods, average_speed, selection, 'limegreen')
        count_chart.draw_bar_chart(periods, counts, selection, 'gold', integer=True)
        plotinfo.grid(row=0, column=0, sticky=(tk.W + tk.E))


class StackedBarChartView(tk.Frame):
    def __init__(self, parent, table_name,
                 days_of_week, weekly_distances,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.table_name = table_name
        self.days_of_week = days_of_week
        self.weekly_distances = weekly_distances

        # stacked bar chart title
        title_name = ' '.join(split(r'[\-_+.]', self.table_name))

        # bar chart plots
        plotinfo = tk.LabelFrame(self, text='Marathon program', padx=5, pady=5)
        distance_chart = w.BarChartWidget(self, "Week number", "Weekly distances (km)",
                                          "Weekly progression for " + title_name +
                                          " marathon training program", figsize=(15, 10))
        distance_chart.grid(row=0, column=0, sticky=(tk.W + tk.E))
        distance_chart.draw_stacked_bar_chart(self.days_of_week, self.weekly_distances)
        plotinfo.grid(row=0, column=0, sticky=(tk.W + tk.E))
