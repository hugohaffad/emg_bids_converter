"""Entry point of the emg-bids-gui command"""

from .home import Home


def main() -> None:
    """Open the main window and run the Tkinter event loop until it is closed"""
    home = Home()
    home.mainloop()


if __name__ == "__main__":
    main()
