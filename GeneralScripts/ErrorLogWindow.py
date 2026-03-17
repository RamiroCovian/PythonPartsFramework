"""
Implementation of the error log window
"""

from tkinter import *
from tkinter import scrolledtext


def create_error_log_window():
    if not "error_log_window" in globals():
        globals()["error_log_window"] = LogWindow()


def clear_error_log_window():
    if "error_log_window" in globals():
        globals()["error_log_window"].clear()

 
class LogWindow():
    def __init__(self):
        self.window = Tk()
 
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
 
        frame = Frame(self.window, bd=2, relief=SUNKEN)
        frame.pack(fill='both', expand='yes')
 
        self.text_area = scrolledtext.ScrolledText(frame, wrap=WORD, bd=0, width=200, height = 50)
 
        self.text_area.pack(fill=BOTH, expand=True)

        self.window.update()
 
        self.stderr = sys.stderr
 
        sys.stderr = StdoutDirector(self.text_area)

 
    def clear(self):
        self.text_area.delete("1.0" , END)
        self.window.update()

 
    def on_close(self):
        sys.stderr = self.stderr
 
        self.window.destroy()

        globals()["error_log_window"] = None
 
 
class IODirector(object):
    def __init__(self, text_area):
        self.text_area = text_area
 
 
class StdoutDirector(IODirector):
    def write(self, msg):
        self.text_area.insert(END, msg)
        self.text_area.see(END)
        self.text_area.update()
 
    def flush(self):
        pass

