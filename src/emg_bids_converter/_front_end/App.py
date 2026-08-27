from tkinter import Tk

class App(Tk):
    def __init__(self):
        super().__init__()

        self.withdraw()
        self.mainloop()