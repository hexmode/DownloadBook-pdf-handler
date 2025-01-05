"""A simple GUI interface for the CLI."""

import logging
import os
import subprocess
import threading
import tkinter as tk
from queue import Empty, Queue
from ssl import SSLCertVerificationError
from tkinter import Button, Event, Label, Toplevel, messagebox

from httpx import ConnectError

from src.exceptions import LoginCredsNeededError, MissingSettingError
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
        """
        Set up widgets for the application.

        This method creates and places various UI such as labels,
        entry fields, text widget for logs, and buttons for saving configuration
        and printing collection.
        """
        row = 0
        Label(self.root, text="WIKI_API_URL").grid(row=row, column=0)
        self.wiki_api_url_var = tk.StringVar()
        self.wiki_api_url_var.trace("w", lambda *args: self.apply_setting("WIKI_API_URL"))
        self.wiki_api_url_entry = tk.Entry(self.root, width=50, textvariable=self.wiki_api_url_var)
        self.wiki_api_url_entry.grid(row=row, column=1)

        row += 1
        Label(self.root, text="WIKI_CA_CERT").grid(row=row, column=0)
        self.wiki_ca_cert_var = tk.StringVar()
        self.wiki_ca_cert_var.trace("w", lambda *args: self.apply_setting("WIKI_CA_CERT"))
        self.wiki_ca_cert_entry = tk.Entry(self.root, width=50, textvariable=self.wiki_ca_cert_var)
        self.wiki_ca_cert_entry.grid(row=row, column=1)

        row += 1
        Label(self.root, text="WIKI_USER").grid(row=row, column=0)
        self.wiki_user_var = tk.StringVar()
        self.wiki_user_var.trace("w", lambda *args: self.apply_setting("WIKI_USER"))
        self.wiki_user_entry = tk.Entry(self.root, width=50, textvariable=self.wiki_user_var)
        self.wiki_user_entry.grid(row=row, column=1)

        row += 1
        Label(self.root, text="WIKI_PASS").grid(row=row, column=0)
        self.wiki_pass_var = tk.StringVar()
        self.wiki_pass_var.trace("w", lambda *args: self.apply_setting("WIKI_PASS"))
        self.wiki_pass_entry = tk.Entry(self.root, width=50, textvariable=self.wiki_pass_var)
        self.wiki_pass_entry.grid(row=row, column=1)

        row += 1
        Label(self.root, text="URL_PREFIX").grid(row=row, column=0)
        self.url_prefix_var = tk.StringVar()
        self.url_prefix_var.trace("w", lambda *args: self.apply_setting("URL_PREFIX"))
        self.url_prefix_entry = tk.Entry(self.root, width=50, textvariable=self.url_prefix_var)
        self.url_prefix_entry.grid(row=row, column=1)

        row += 1
        Label(self.root, text="COLLECTION_TITLE").grid(row=row, column=0)
        self.collection_title_var = tk.StringVar()
        self.collection_title_var.trace("w", lambda *args: self.apply_setting("COLLECTION_TITLE"))
        self.collection_title_entry = tk.Entry(self.root, width=50, textvariable=self.collection_title_var)
        self.collection_title_entry.grid(row=row, column=1)

        row += 1
        Label(self.root, text="WIKI_BOOK_PAGE").grid(row=row, column=0)
        self.wiki_book_page_var = tk.StringVar()
        self.wiki_book_page_var.trace("w", lambda *args: self.apply_setting("WIKI_BOOK_PAGE"))
        self.wiki_book_page_entry = tk.Entry(self.root, width=50, textvariable=self.wiki_book_page_var)
        self.wiki_book_page_entry.grid(row=row, column=1)

        # Add a Text widget for log output
        row += 1
        self.log_text = tk.Text(self.root, height=10, width=60)
        self.log_text.grid(row=row, columnspan=10, sticky="nsew")

        # Configure grid weights to allow the text widget to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        row += 1
        save_button = Button(self.root, text="Save", command=self.save_config)
        save_button.grid(row=row, columnspan=2)

        row += 1
        print_button = Button(self.root, text="Print Collection", command=self.print_collection)
        print_button.grid(row=row, columnspan=2)

        self.root.bind("<Return>", self.print_collection)

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
