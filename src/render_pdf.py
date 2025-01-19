"""A simple GUI interface for the CLI."""

import logging
import os
import subprocess
import threading
import tkinter as tk
import traceback
from queue import Empty, Queue
from ssl import SSLCertVerificationError
from tkinter import Button, Event, Label, Toplevel, messagebox

from httpx import ConnectError
from mwclient.errors import APIError, LoginError, MaximumRetriesExceeded
from requests.exceptions import ConnectionError as RequestConnectionError

from src.exceptions import (
    LoginCredsNeededError,
    MissingSettingError,
    NoLinkFoundError,
    NoPageListPageError,
)
from src.print_mw_collection import main as print_mw_collection
from src.settings import Settings
from src.text_handler import TextHandler


class SimpleUI:
    """
    Implementation of a simple UI.

    Parameters
    ----------
    root : tk.Tk
        The root window of the application.
    """

    current_row = 0

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

        # Start the UI update loop to display logs
        self.root.after(100, self.update_ui)

        self.setting = Settings()
        self.load_defaults()

    def apply_setting(self, setting_name: str) -> None:
        """
        Set the setting value.

        Parameters
        ----------
        setting_name : str
            The name of the setting to update.
        """
        value = getattr(self, f"{setting_name.lower()}_var").get()
        self.setting.set_value(setting_name, value)

    def create_widgets(self) -> None:
        """Set up widgets for the application."""
        self.add_entry_widget("WIKI_API_URL")
        self.add_entry_widget("WIKI_CA_CERT")
        self.add_entry_widget("WIKI_USER")
        self.add_entry_widget("WIKI_PASS", "•")
        self.add_entry_widget("URL_PREFIX")
        self.add_entry_widget("COLLECTION_TITLE")
        self.add_entry_widget("WIKI_BOOK_PAGE")

        # Add a Text widget for log output
        self.current_row += 1
        self.log_text = tk.Text(self.root, height=10, width=60)
        self.log_text.grid(row=self.current_row, columnspan=10, sticky="nsew")

        # Configure grid weights to allow the text widget to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.current_row += 1
        save_button = Button(self.root, text="Save", command=self.save_config)
        save_button.grid(row=self.current_row, columnspan=2)

        self.current_row += 1
        print_button = Button(self.root, text="Print Collection", command=self.print_collection)
        print_button.grid(row=self.current_row, columnspan=2)

        self.root.bind("<Return>", self.print_collection)

    def add_entry_widget(self, label_text: str, shown: str = "") -> None:
        """
        Create a labeled entry widget and add it to the grid.

        Parameters
        ----------
        label_text : str
            The label for the entry.
        shown : str
            The character to show for input.  Default is "" to show provided input.
        """
        Label(self.root, text=label_text).grid(row=self.current_row, column=0)
        var_name = f"{label_text.lower()}_var"
        entry_name = f"{label_text.lower()}_entry"
        setattr(self, var_name, tk.StringVar())
        getattr(self, var_name).trace("w", lambda *args: self.apply_setting(label_text))
        setattr(self, entry_name, tk.Entry(self.root, width=50, textvariable=getattr(self, var_name), show=shown))
        getattr(self, entry_name).grid(row=self.current_row, column=1)
        self.current_row += 1

    def parse_line(self, line: str) -> None:
        """
        Handle an individual line in the settings file.

        Parameters
        ----------
        line : str
            A single line from the settings file. This line may contain a key-value pair separated
            by an equal sign (`=`), as well as optional comments delimited by a `#` character.
        """
        line = line.split("#", 1)[0].strip()
        if "=" in line and line:
            key, value = line.split("=", 1)

            if hasattr(self, f"{key.lower()}_entry"):
                setattr(self.setting, key.lower(), value)
                getattr(self, f"{key.lower()}_entry").insert(0, value)

    def load_defaults(self) -> None:
        """
        Load the defaults from .env file if it exists.

        This method checks if a .env file exists in the current directory.
        If it does, it reads the file line by line and processes each line
        using the `parse_line` method. After loading the configuration,
        a confirmation message is logged.
        """
        if os.path.exists(".env"):
            with open(".env", encoding="utf-8") as env_file:
                for line in env_file:
                    self.parse_line(line)

            self.logger.info("Loaded default configuration from .env file")

    def save_config(self) -> None:
        """
        Save any changes to the configuration.

        This method gathers data from various entry fields, constructs a
        configuration dictionary, and writes it to a file named `.env`.
        Each configuration key and its corresponding value are saved
        line by line in the file. Finally, a success message is logged.
        """
        with open(".env", "w", encoding="utf-8") as env_file:
            for key, _ in self.setting.value_map.items():
                attr = getattr(self, key.lower() + "_entry")
                value = attr.get()
                env_file.write(f"{key}={value}\n")
            self.logger.info("Configuration saved successfully")

    def make_pdf(self) -> None:
        """Generate a PDF from the relevant collection and notify the user."""
        try:
            self.notify_user(print_mw_collection(self.logger, self.setting))
        except LoginCredsNeededError:
            messagebox.showerror("Login", "Login credentials are needed.  Try visiting Special:BotPasswords.")
        except RequestConnectionError as e:
            if "No route to host" in str(e):
                messagebox.showerror("Connection error", "No route to host: Is there a typo in the URL?")
        except OSError as e:
            messagebox.showerror("Error", str(e))
        except MissingSettingError as e:
            messagebox.showerror("Missing Setting", f"Please provide the {e}")
        except ConnectError as e:
            if isinstance(e.__cause__, SSLCertVerificationError):
                messagebox.showerror(
                    "SSL Certificate Verification Failed",
                    'Secure connection failed.  Either provide an SSL Cert in WIKI_CA_CERT or enter "false".',
                )
        except APIError as e:
            if e.code == "readapidenied":
                messagebox.showerror("Login", f"Error accessing API ({e.code}).  Try visiting Special:BotPasswords.")
        except LoginError as e:
            self.logger.error(str(e))
            messagebox.showerror("Login Error", str(e))
        except MaximumRetriesExceeded as e:
            self.logger.error(str(e))
            messagebox.showerror("Maximum Retries Exceeded", str(e))
        except NoLinkFoundError as e:
            messagebox.showerror("Page structure problem", f"This line does not look like a link: <{e}>")
        except NoPageListPageError:
            messagebox.showerror("Wiki Book Page", "Trouble getting the WIKI_BOOK_PAGE.")
        except Exception as e:  # pylint: disable=W0718
            self.logger.warning("Uncaught exception of type %s", type(e))
            self.logger.warning("Exception message: %s", str(e))
            self.logger.debug("Backtrace:\n%s", traceback.format_exc())

    def print_collection(self, _: Event | None = None) -> None:
        """
        Call printing.

        Parameters
        ----------
        _ : placeholder
            Ignored.
        """
        self.logger.info("Printing collection...")

        # Start the background task in a separate thread
        thread = threading.Thread(target=self.make_pdf)
        thread.daemon = True
        thread.start()

    def find_pdf_handler_and_open(self, file_path: str) -> None:
        """
        Open a PDF file using the default PDF handler on the system.

        Parameters
        ----------
        file_path : str
            The path of the PDF file to be opened.

        Notes
        -----
        - On Windows systems, this function uses `os.startfile`.
        - On macOS and Linux systems, it uses the `xdg-open` command.
        """
        try:
            if hasattr(os, "startfile"):
                os.startfile(file_path)
            elif os.name == "posix":  # For macOS and Linux
                subprocess.run(["/usr/bin/xdg-open", file_path], check=True)
        except Exception as e:  # pylint: disable=W0718
            self.logger.error("Error while opening the file: %s", e)

    def notify_user(self, pdf_file: str) -> None:
        """
        Notify the user with a dialog.

        Parameters
        ----------
        pdf_file : str
            The pdf file to view (if requested).
        """

        def view_pdf() -> None:
            """View the PDF."""
            self.find_pdf_handler_and_open(pdf_file)

        def return_to_root() -> None:
            """Go back to the main window."""
            dialog.destroy()
            self.root.deiconify()

        def quit_application() -> None:
            """Quit the application."""
            self.root.destroy()

        self.root.withdraw()  # Hide the main window
        dialog = Toplevel(self.root)
        dialog.title("Notification")

        Label(dialog, text=f"PDF creation is complete!\nSee {pdf_file}.").pack(pady=10)

        Button(dialog, text="Quit", command=quit_application).pack(side="left", padx=20, pady=20)
        Button(dialog, text="View PDF", command=view_pdf).pack(side="left", padx=20, pady=20)
        Button(dialog, text="Return", command=return_to_root).pack(side="left", padx=20, pady=20)

    def setup_logger(self) -> None:
        """
        Set up a logger for the SimpleUI application.

        This method initializes a logger for the application, configures its level,
        sets up a custom formatter, and attaches a TextHandler for logging output.
        """
        # Set up a basic logger
        self.logger = logging.getLogger("SimpleUI")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        th = TextHandler(self.root, self.log_text)
        th.setLevel(logging.DEBUG)
        th.setFormatter(formatter)

        # Add the text handler to the logger
        self.logger.addHandler(th)

    def update_ui(self) -> None:
        """
        Update the user interface.

        Fetch log messages from the queue and appending them to the log text widget. The
        method checks the queue non-blocking and schedules itself to run again after a specified interval.
        """
        try:
            # Get log message from the queue (non-blocking)
            while True:
                message: str = Queue().get_nowait()  # Try to get a message from the queue
                self.log_text.config(state=tk.NORMAL)  # Enable editing of the text widget
                self.log_text.insert(tk.END, message + "\n")  # Insert the log message
                self.log_text.yview(tk.END)  # Scroll to the bottom
                self.log_text.config(state=tk.DISABLED)  # Disable editing again
        except Empty:  # Correct exception handling (use Empty, not queue.Empty)
            pass
        self.root.after(100, self.update_ui)  # Check again in 100ms


def main() -> None:
    """Drive the application."""
    root = tk.Tk()
    SimpleUI(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
