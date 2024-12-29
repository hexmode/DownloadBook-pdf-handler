"""A simple GUI interface for the CLI."""

import logging
import os
import tkinter as tk

from src.print_mw_collection import main as print_mw_collection


# Redirect logs to the Text widget
class TextHandler(logging.Handler):
    """Send log to the window."""

    def __init__(self, root: tk.Tk, log_text: tk.Text):
        """
        Initialize the logger class.

        Parameters
        ----------
        text : tk.Text
            The root window of the application.
        """
        super().__init__()
        self.root = root
        self.log_text = log_text

    def emit(self, record: logging.LogRecord) -> None:
        """Send the record to the window."""
        log_entry = self.format(record)
        self.root.after(0, lambda: self.log_text.insert(tk.END, log_entry + "\n"))
        self.log_text.see(tk.END)


class SimpleUI:
    """Implementation of a simple UI."""

    def __init__(self, root: tk.Tk):
        """
        Initialize the SimpleUI class.

        Parameters
        ----------
        root : tk.Tk
            The root window of the application.
        """
        self.root = root
        self.root.title("PDF Handler")

        self.create_widgets()
        self.setup_logger()
        self.load_defaults()

    def create_widgets(self) -> None:
        """
        Set up widgets for the application.

        This method creates and places various UI such as labels,
        entry fields, text widget for logs, and buttons for saving configuration
        and printing collection.
        """
        tk.Label(self.root, text="WIKI_API_URL").grid(row=0, column=0)
        self.wiki_api_url_entry = tk.Entry(self.root, width=50)
        self.wiki_api_url_entry.grid(row=0, column=1)

        tk.Label(self.root, text="URL_PREFIX").grid(row=1, column=0)
        self.url_prefix_entry = tk.Entry(self.root, width=50)
        self.url_prefix_entry.grid(row=1, column=1)

        tk.Label(self.root, text="COLLECTION_TITLE").grid(row=2, column=0)
        self.collection_title_entry = tk.Entry(self.root, width=50)
        self.collection_title_entry.grid(row=2, column=1)

        tk.Label(self.root, text="WIKI_BOOK_PAGE").grid(row=3, column=0)
        self.wiki_book_page_entry = tk.Entry(self.root, width=50)
        self.wiki_book_page_entry.grid(row=3, column=1)

        # Add a Text widget for log output
        self.log_text = tk.Text(self.root, height=10, width=60)
        self.log_text.grid(row=6, columnspan=10, sticky="nsew")

        # Configure grid weights to allow the text widget to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        save_button = tk.Button(self.root, text="Save", command=self.save_config)
        save_button.grid(row=4, columnspan=2)

        print_button = tk.Button(self.root, text="Print Collection", command=self.print_mw_collection)
        print_button.grid(row=5, columnspan=2)

    def load_defaults(self) -> None:
        """Load the defaults from .env if it exists."""
        if os.path.exists(".env"):
            with open(".env", "r", encoding="utf-8") as env_file:
                for line in env_file:
                    key, value = line.strip().split("=", 1)
                    if hasattr(self, f"{key.lower()}_entry"):
                        getattr(self, f"{key.lower()}_entry").insert(0, value)
            self.logger.info("Loaded default configuration from .env file")

    def save_config(self) -> None:
        """Save any changes to the configuration."""
        config = {
            "WIKI_API_URL": self.wiki_api_url_entry.get(),
            "URL_PREFIX": self.url_prefix_entry.get(),
            "COLLECTION_TITLE": self.collection_title_entry.get(),
            "WIKI_BOOK_PAGE": self.wiki_book_page_entry.get()
        }

        with open(".env", "w", encoding="utf-8") as env_file:
            for key, value in config.items():
                env_file.write(f"{key}={value}\n")
            self.logger.info("Configuration saved successfully")

    def print_mw_collection(self) -> None:
        """Call printing."""
        self.logger.info("Printing collection...")
        # Add your actual logic here
        print_mw_collection(self.logger)

    def setup_logger(self) -> None:
        """Set up a logger."""
        # Set up a basic logger
        self.logger = logging.getLogger("SimpleUI")
        self.logger.setLevel(logging.DEBUG)

        # Create a console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        th = TextHandler(self.root, self.log_text)
        th.setLevel(logging.DEBUG)
        th.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(th)


def main() -> None:
    """Drive the application."""
    root = tk.Tk()
    SimpleUI(root)
    root.mainloop()
