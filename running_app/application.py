import tkinter as tk
from tkinter import ttk


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
