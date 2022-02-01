import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from . import widgets as w


class MainMenu(tk.Menu):
    '''The Application's main menu'''

    def __init__(self, parent, callbacks, *args, **kwargs):
        '''Constructor for MainMenu

        arguments:
            parent - the parent widget
            callbacks - a dict containing Python callbacks
            settings - dict to save user settings
        '''
        super().__init__(parent, *args, **kwargs)

        # the file menu
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(
            # 8230: ASCII value for horizontal ellipsis
            label='Import file with running data'+chr(8230),
            command=callbacks['file->import']
            )
        file_menu.add_command(
            # 8230: ASCII value for horizontal ellipsis
            label='Export file with running data'+chr(8230),
            command=callbacks['file->export']
            )
        self.add_cascade(label='File', menu=file_menu)
        file_menu.add_separator()
        stats_menu = tk.Menu(file_menu, tearoff=False)
        file_menu.add_cascade(label='Show statistics', menu=stats_menu)
        stats_menu.add_command(
            label='Show running progression',
            command=callbacks['on_show_running_progression']
            )
        stats_menu.add_command(
            label='Show VO2Max',
            command=callbacks['on_show_vo2max']
            )

        # the help menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='About'+chr(8230), command=self.show_about)
        self.add_cascade(label='Help', menu=help_menu)

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
                                           field_spec=fields['Date'],)
        self.inputs['Date'].grid(row=0, column=0)
        self.inputs['Time'] = w.LabelInput(runninginfo, 'Time (hh:mm:ss)',
                                           field_spec=fields['Time'],)
        self.inputs['Time'].grid(row=0, column=1)
        self.inputs['Distance'] = w.LabelInput(runninginfo, 'Distance (km)',
                                               field_spec=fields['Distance'])
        self.inputs['Distance'].grid(row=0, column=2)
        self.inputs['Location'] = w.LabelInput(runninginfo, 'Location (City, Country)',
                                               field_spec=fields['Location'])
        self.inputs['Location'].grid(row=0, column=3)
        runninginfo.grid(row=1, column=0, sticky=(tk.W + tk.E))

        # command section
        command_section = tk.LabelFrame(self, text='Commands', padx=5, pady=5)
        self.insertbutton = w.LabelInput(command_section, 'Add / update data',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_insert'])
        self.insertbutton.grid(row=0, column=0, padx=10, pady=(10, 0))
        self.removebutton = w.LabelInput(command_section, 'Remove data',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_remove'])
        self.removebutton.grid(row=0, column=1, padx=10, pady=(10, 0))
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

    def load_record(self, rowkey, data=None):
        self.record_label.config(text='Date: {}'.format(rowkey))
        for key, widget in self.inputs.items():
            self.inputs[key].set(data.get(key, ''))
            try:
                widget.input.trigger_focusout_validation()
            except AttributeError:
                pass


class RecordList(tk.Frame):
    '''Display records in the database'''

    column_defs = {
        '#0': {'label': 'Row', 'anchor': tk.W},
        'Date': {'label': 'Date (YYYY-mm-dd)', 'width': 160},
        'Time': {'label': 'Time (hh:mm:ss)', 'width': 160},
        'Distance': {'label': 'Distance (km)', 'width': 120},
        'Pace': {'label': 'Pace (min/km)', 'width': 120},
        'Location': {'label': 'Location (City, Country)', 'width': 240},
    }
    default_width = 100
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

        # bind selection
        self.treeview.bind('<<TreeviewSelect>>', self.on_open_record)

    def on_open_record(self, *args):
        try:
            selected_id = self.treeview.selection()[0]
            self.callbacks['on_open_record'](selected_id.split('|')[0])
        # quick fix when window loses focus and no line is selected,
        # a better fix is to find a way to keep the line selected
        except IndexError:
            pass

    def populate(self, rows):
        '''Clear the treeview and write the supplied data rows to it'''

        for row in self.treeview.get_children():
            self.treeview.delete(row)

        valuekeys = list(self.column_defs.keys())[1:]
        for rowdata in rows:
            rowkey = (str(rowdata['Date']), str(rowdata['Time']),
                      str(rowdata['Distance']), str(rowdata['Pace']),
                      str(rowdata['Location']))
            values = [rowdata[key] for key in valuekeys]
            if self.inserted and rowkey in self.inserted:
                tag = 'inserted_record'
            elif self.updated and rowkey in self.updated:
                tag = 'updated_record'
            else:
                tag = ''
            stringkey = '{}|{}|{}|{}|{}'.format(*rowkey)
            self.treeview.insert('', 'end', iid=stringkey, text=stringkey,
                                 values=values, tag=tag)

        # selects automatically the first row, to make selections keyboard-friendly
        if len(rows) > 0:
            firstrow = self.treeview.identify_row(0)
            self.treeview.focus_set()
            self.treeview.selection_set(firstrow)
            self.treeview.focus(firstrow)
