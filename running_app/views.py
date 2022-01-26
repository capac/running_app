import tkinter as tk
from tkinter import ttk
from . import widgets as w


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
        self.inputs['Time'] = w.LabelInput(runninginfo, 'Time (h:m:s)',
                                           field_spec=fields['Time'],)
        self.inputs['Time'].grid(row=0, column=1)
        self.inputs['Distance'] = w.LabelInput(runninginfo, 'Distance (km)',
                                               field_spec=fields['Distance'])
        self.inputs['Distance'].grid(row=0, column=2)
        self.inputs['Location'] = w.LabelInput(runninginfo, 'Location',
                                               field_spec=fields['Location'])
        self.inputs['Location'].grid(row=0, column=3)
        runninginfo.grid(row=1, column=0, sticky=(tk.W + tk.E))

        # command section
        command_section = tk.LabelFrame(self, text='Commands', padx=5, pady=5)
        self.updatebutton = w.LabelInput(command_section, 'Save data',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_save'])
        command_section.grid(row=2, column=0, sticky=(tk.W + tk.E))
