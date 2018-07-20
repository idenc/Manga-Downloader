import tkinter as tk
from tkinter.ttk import Progressbar
import queue


class Display:
    """Handles display for manga downloader"""

    def __init__(self, queue):
        self.start_label = None
        self.start_entry = None
        self.end_label = None
        self.end_entry = None
        self.go_button = None
        self.info_label = None
        self.root = None
        self.progress = None
        self.queue = queue
        self.create_window()

    def create_window(self):
        """Creates window for manga downloader"""
        self.root = tk.Tk()
        self.root.title("Manga Downloader")
        self.root.geometry("400x200")

        parent = tk.Frame(self.root)

        # Gets the requested values of the height and width.
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        position_right = int(self.root.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(self.root.winfo_screenheight() / 2 - window_height / 2)

        # Positions the window in the center of the page.
        self.root.geometry("+{}+{}".format(position_right, position_down))

        # Widgets
        self.start_label = tk.Label(parent, text="Start link:")
        self.start_entry = tk.Entry(parent)
        self.end_label = tk.Label(parent, text="End link:\n(Leave blank to download entire manga)")
        self.end_entry = tk.Entry(parent)
        self.go_button = tk.Button(parent, text="Go", fg="#a1dbcd", bg="#383a39")
        self.info_label = tk.Label(self.root, text="Hello!", bd=1, relief='sunken', anchor='w')
        self.progress = Progressbar(parent, orient='horizontal', mode='indeterminate')

        # Pack widgets
        self.start_label.pack(fill='x')
        self.start_entry.pack(fill='x')
        self.end_label.pack(fill='x')
        self.end_entry.pack(fill='x')
        self.go_button.pack(padx=20, pady=20, fill='x')
        self.info_label.pack(side='bottom', fill='x')
        parent.pack()

    def process_incoming(self):
        """Handle all the messages currently in the queue (if any)."""
        while not self.queue.empty():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                self.info_label.config(text=msg)
            except queue.Empty:
                pass
