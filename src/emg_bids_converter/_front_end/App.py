from tkinter import Tk
from emg_bids_converter._front_end.Home import Home

class App(Tk):
    """Instantiates the application"""
    def __init__(self):
        super().__init__()
        self.withdraw()
        Home(self)