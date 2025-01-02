"""Settings for everything."""

import logging
import os
from collections import namedtuple
from urllib.parse import urlparse

from dotenv import load_dotenv
from mwclient import Site
from requests import Session

from src.structure import WikiPage, get_ordered_wiki_pages, populate_book

load_dotenv()
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

TocOffset = namedtuple("TocOffset", ["title", "level"])


class Settings:
    """Class to carry the settings around."""

    # fmt: off                      # EnvVar           Description
    api_url: str | None  # WIKI_API_URL     The API URL (i.e. http://example.wiki/w/api.php).
    url_prefix: str | None  # URL_PREFIX       The prefix before each page (i.e. http://example.wiki/wiki/).
    username: str | None  # WIKI_USER        The username for the wiki, if any.
    password: str | None  # WIKI_PASS        The password for the username.
    verify: str | None  # WIKI_CA_CERT     The path to the certificate authority's cert
    #                  (if you have a custom CA or self signed cert).
    title: str | None  # COLLECTION_TITLE The title for the book being produced. This will be used for the
    #                  filename as well as in the produced PDF.
    page_list_page: str | None  # WIKI_BOOK_PAGE   The title of the wikipage that contains the the book.
    pages: list[TocOffset] | None  #                  List of pages from the page_list_page
    site: Site | None  #                  The mwclient object for the wiki
    # fmt: on

    def __init__(self) -> None:
        """Initialize."""
        # Define your credentials and MediaWiki API endpoint
        self.load()

    def load(self) -> None:
        """Get settings from the environment."""
        self.api_url = os.getenv("WIKI_API_URL")
        self.url_prefix = os.getenv("URL_PREFIX")
        self.username = os.getenv("WIKI_USER")
        self.password = os.getenv("WIKI_PASS")
        self.verify = os.getenv("WIKI_CA_CERT")
        self.title = os.getenv("COLLECTION_TITLE")
        self.page_list_page = os.getenv("WIKI_BOOK_PAGE")

    def get_site(self) -> Site:
        """
        Retrieve or initialize a `Site` object.

        This function checks if the global `_site` object has already been created.
        If not, it initializes a new `Site` instance based on the parsed `api_url`.
        Specifically, it extracts the schema, domain, and path from the `api_url`
        and uses them to instantiate a new `Site` object.

        Returns
        -------
        Site
            An instance of the `Site` class that represents the current website
            being used.
        """
        if not hasattr(self, "site"):
            parsed = urlparse(self.api_url)
            scheme = parsed.scheme
            host = parsed.netloc
            path: str | bytes = ""
            if isinstance(parsed.path, bytes):
                path = parsed.path.removesuffix(b"api.php")
            elif isinstance(parsed.path, str):
                path = parsed.path.removesuffix("api.php")

            self.site = Site(host, scheme=scheme, path=path)

            if self.verify is not None:
                session = Session()
                session.verify = self.verify
                self.site = Site(host, scheme=scheme, path=path, pool=session)

        return self.site

    def get_page_list_pages(self) -> list[WikiPage]:
        """
        Retrieve and return a list of ordered WikiPage objects.

        This function performs the following operations:
        1. Retrieves the site object and accesses the `page_list_page` entry.
        2. Populates a book structure based on the retrieved page.
        3. Extracts and returns the ordered WikiPage objects from the book.

        Returns
        -------
        list[WikiPage]
            A list of WikiPage objects in the intended order.
        """
        page = self.get_site().pages[self.page_list_page]
        book = populate_book(page.text())
        return get_ordered_wiki_pages(book)

    def get_pages(self) -> list[TocOffset]:
        """Retrieve the page list from the wiki."""
        return [TocOffset(title=page.link.url, level=page.level) for page in self.get_page_list_pages()]


class MissingSettingError(Exception):
    """Signal that a setting is missing."""
