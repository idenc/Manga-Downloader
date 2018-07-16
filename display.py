from tkinter import *


class Display:

    def __init__(self):
        self.start_label = None
        self.start_entry = None
        self.end_label = None
        self.end_entry = None
        self.go_button = None
        self.root = None
        self.create_window()

    def create_window(self):
        """Creates window for manga downloader"""
        self.root = Tk()
        self.root.title("Manga downloader")
        self.root.geometry("300x300")

        parent = Frame(self.root)

        # Gets the requested values of the height and width.
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        position_right = int(self.root.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(self.root.winfo_screenheight() / 2 - window_height / 2)

        # Positions the window in the center of the page.
        self.root.geometry("+{}+{}".format(position_right, position_down))

        # Widgets
        self.start_label = Label(parent, text="Start link:")
        self.start_entry = Entry(parent)
        self.end_label = Label(parent, text="End link:\n(Leave blank to download entire manga)")
        self.end_entry = Entry(parent)
        self.go_button = Button(parent, text="Go")

        # Pack widgets
        self.start_label.pack(fill='x')
        self.start_entry.pack(fill='x')
        self.end_label.pack(fill='x')
        self.end_entry.pack(fill='x')
        self.go_button.pack(fill='x')
        parent.pack(expand=1)
