from tkinter import *
from tkinter import filedialog
from tkinter import ttk

from emg_bids_converter._front_end.NewDatasetWindow import NewDatasetWindow
from emg_bids_converter._front_end.App import App

from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("emg_bids_converter")
except PackageNotFoundError:
    __version__ = "dev"

"""HOME WINDOW"""
class Home(Toplevel):
    """Instantiates a Home window"""
    def __init__(self, parent: "App") -> None:
        super().__init__(parent)
        self.parent = parent
        self._configure_window()
        self._build_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    """Window configuration"""
    def _configure_window(self) -> None:
        # Title
        self.title("Home")

        # Geometry
        screen_h = self.winfo_screenheight()
        screen_w = self.winfo_screenwidth()
        window_h = screen_h // 2
        window_w = window_h
        x = (screen_w - window_w) // 2
        y = (screen_h - window_h) // 2
        self.geometry(f'{window_w}x{window_h}+{x}+{y}')
        self.resizable(width=False, height=False)
        self.attributes('-topmost', True)

    """Widgets"""
    def _build_widgets(self) -> None:
        # Menu bar
        self._build_menu_bar()
        self._build_header()
        self._build_body()

    def _build_menu_bar(self) -> None:
        menu_bar = Menu(self)

        file_menu = Menu(menu_bar, tearoff=False)
        file_menu.add_command(label='New dataset...', command=self._on_new_dataset)
        file_menu.add_command(label='Quit', command=self._on_close)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.config(menu=menu_bar)

    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill=X, pady=150)

        title = ttk.Label(
            header,
            text="EMG-BIDS converter",
            font=("Arial", 24, "bold")
        )
        title.pack()

        subtitle = ttk.Label(
            header,
            text=(
                f"EMG-BIDS converter (version {__version__}) is an open-source software for "
                "converting EMG recordings into "
                "the EMG-BIDS standard format, running in Python."
            ),
            font=("Arial", 16),
            foreground="gray30",
            wraplength=400,
            justify=CENTER
        )
        subtitle.pack(pady=(50, 0))

        copyright_label = ttk.Label(
            header,
            text="Copyright (c) 2026 H. Haffad, ToNIC Laboratory, UMR 1214, Inserm / Toulouse University",
            font=("Arial", 14),
            foreground="gray50",
            wraplength=400,
            justify=CENTER
        )
        copyright_label.pack(pady=(20, 0))

    def _build_body(self) -> None:
        buttons = ttk.Frame(self)
        buttons.pack()

        new_dataset_btn = ttk.Button(
            buttons,
            text="New dataset",
            command=self._on_new_dataset,
            width=20
        )
        new_dataset_btn.grid(row=0, column=0, padx=10)

        load_dataset_btn = ttk.Button(
            buttons,
            text="Load a dataset",
            command=self._on_load_dataset,
            width=20
        )
        load_dataset_btn.grid(row=0, column=1, padx=10)

    """Commands"""
    def _on_new_dataset(self) -> None:
        NewDatasetWindow(self)

    def _on_close(self):
        self.parent.destroy()

    def _on_load_dataset(self) -> None:
        folder_path = filedialog.askdirectory(
            parent=self,
            title="Select a dataset folder"
        )

        if not folder_path:
            return