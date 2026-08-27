from tkinter import *
from emg_bids_converter._front_end.Home import *

class App(Tk):
    """Instantiates an App window"""
    def __init__(self):
        super().__init__()
        self.withdraw()
        Home(self)