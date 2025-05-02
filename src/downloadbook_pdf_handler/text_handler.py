"""Redirect logs to the Text widget."""

import logging
import tkinter as tk


class TextHandler(logging.Handler):
    """
    Send log to the window.

    Parameters
    ----------
    root : tk.Tk
        The root window of the application.
    log_text : tk.Text
        The text panel which will show the logging.
    """

    def __init__(self, root: tk.Tk, log_text: tk.Text):
        """
        Initialize the logger class.

        Parameters
        ----------
        root : tk.Tk
            The root window of the application.
        log_text : tk.Text
            The text panel which will show the logging.
        """
        super().__init__()
        self.root = root
        self.log_text = log_text

    def emit(self, record: logging.LogRecord) -> None:
        """
        Send the record to the window.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to be sent to the window.
        """
        log_entry = self.format(record)
        self.root.after(0, lambda: self.log_text.insert(tk.END, log_entry + "\n"))
        self.log_text.see(tk.END)
