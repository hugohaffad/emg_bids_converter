"""Main window of the graphical interface"""

from tkinter import *


class Home(Tk):
    """Main window: entry point to create a dataset or add a recording"""

    def __init__(self) -> None:
        super().__init__()
        self.title("EMG-BIDS Converter")
