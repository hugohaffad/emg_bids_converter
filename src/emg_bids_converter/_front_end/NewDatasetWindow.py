from tkinter import *
from tkinter import ttk
from emg_bids_converter._front_end.Home import Home


"""NEW DATASET WINDOW"""
class NewDatasetWindow(Toplevel):
    """Instantiates a New Dataset window"""
    STEPS = [
        "General information",
        "Data import",
        "Conversion",
        "Save"
    ]

    def __init__(self, parent: "Home") -> None:
        super().__init__(parent)
        self.parent = parent
        self.current_step = 0

        self._configure_window()
        self._build_widgets()

    """Window configuration"""
    def _configure_window(self) -> None:
        self.title("New dataset")
        self.transient(self.parent)
        self.resizable(width=False, height=False)

        self.parent.update_idletasks()
        width = self.parent.winfo_width()
        height = self.parent.winfo_height()
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        offset_x = int(x + 0.05 * x)
        offset_y = int(y + 0.1 * y)
        self.geometry(f"{width}x{height}+{offset_x}+{offset_y}")

    """Widgets"""
    def _build_widgets(self) -> None:
        self._build_progress_bar()
        self._build_content_area()
        self._build_navigation()
        self._update_step_display()

    def _build_progress_bar(self) -> None:
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=X, padx=20, pady=(20, 10))

        self.step_labels = []

        for i, step_name in enumerate(self.STEPS):
            step_frame = ttk.Frame(progress_frame)
            step_frame.grid(row=0, column=i, sticky="ew")
            progress_frame.columnconfigure(i, weight=1)

            label = ttk.Label(
                step_frame,
                text=f"{i + 1}. {step_name}",
                font=("Arial", 10),
                anchor=CENTER
            )
            label.pack()
            self.step_labels.append(label)

        self.progress_bar = ttk.Progressbar(
            self,
            orient=HORIZONTAL,
            mode="determinate",
            maximum=len(self.STEPS) - 1
        )
        self.progress_bar.pack(fill=X, padx=20, pady=(0, 10))

    def _build_content_area(self) -> None:
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        self.step_frames = []

        # Step 1: General information
        self.step_frames.append(self._build_step_general_info())

        # Steps 2-4: placeholders for now
        for step_name in self.STEPS[1:]:
            frame = ttk.Frame(self.content_frame)
            placeholder = ttk.Label(
                frame,
                text=f"[{step_name} — content to be defined]",
                font=("Arial", 12),
                foreground="gray50"
            )
            placeholder.pack(expand=True)
            self.step_frames.append(frame)

    def _build_step_general_info(self) -> ttk.Frame:
        frame = ttk.Frame(self.content_frame)

        form = ttk.Frame(frame)
        form.pack(expand=True)

        # Dataset name
        ttk.Label(form, text="Dataset name *", font=("Arial", 11)).grid(
            row=0, column=0, sticky=W, pady=(0, 5)
        )
        self.dataset_name_var = StringVar()
        dataset_name_entry = ttk.Entry(form, textvariable=self.dataset_name_var, width=40)
        dataset_name_entry.grid(row=1, column=0, sticky=EW, pady=(0, 20))

        # Number of subjects
        ttk.Label(form, text="Number of subjects *", font=("Arial", 11)).grid(
            row=2, column=0, sticky=W, pady=(0, 5)
        )
        self.num_subjects_var = IntVar(value=1)
        num_subjects_spinbox = ttk.Spinbox(
            form,
            from_=1,
            to=999,
            textvariable=self.num_subjects_var,
            width=10
        )
        num_subjects_spinbox.grid(row=3, column=0, sticky=W)

        return frame

    def _build_navigation(self) -> None:
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=X, padx=20, pady=20)

        self.prev_btn = ttk.Button(
            nav_frame,
            text="Previous",
            command=self._on_previous
        )
        self.prev_btn.pack(side=LEFT)

        self.next_btn = ttk.Button(
            nav_frame,
            text="Next",
            command=self._on_next
        )
        self.next_btn.pack(side=RIGHT)

    """Step navigation"""
    def _update_step_display(self) -> None:
        # Hide all step frames, show only the current one
        for frame in self.step_frames:
            frame.pack_forget()
        self.step_frames[self.current_step].pack(fill=BOTH, expand=True)

        # Update progress bar
        self.progress_bar["value"] = self.current_step

        # Update step labels styling (bold = current)
        for i, label in enumerate(self.step_labels):
            if i == self.current_step:
                label.config(font=("Arial", 12, "bold"), foreground="black")
            elif i < self.current_step:
                label.config(font=("Arial", 12), foreground="gray30")
            else:
                label.config(font=("Arial", 12), foreground="gray70")

        # Enable/disable navigation buttons
        self.prev_btn.config(state=NORMAL if self.current_step > 0 else DISABLED)
        self.next_btn.config(
            text="Finish" if self.current_step == len(self.STEPS) - 1 else "Next"
        )

    def _on_previous(self) -> None:
        if self.current_step > 0:
            self.current_step -= 1
            self._update_step_display()

    def _on_next(self) -> None:
        if self.current_step < len(self.STEPS) - 1:
            self.current_step += 1
            self._update_step_display()
        else:
            self._on_finish()

    def _on_finish(self) -> None:
        self.destroy()