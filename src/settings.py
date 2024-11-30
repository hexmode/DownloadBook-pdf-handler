"""Settings for everything."""

import logging
import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv
from mwclient import Site
from requests import Session

from src.structure import WikiPage, get_ordered_wiki_pages, populate_book

load_dotenv()
logging.basicConfig()
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# fmt: off
                                # These are set at the end of this file.
                                # EnvVar           Description
api_url: str                    # WIKI_API_URL     The API URL (i.e. http://example.wiki/w/api.php).
username: str | None = None     # WIKI_USER        The username for the wiki, if any.
password: str | None = None     # WIKI_PASS        The password for the username.
verify: str | None = None       # WIKI_CA_CERT     The path to the certificate authority's cert (if you have a custom CA
                                #                  or self signed cert).
title: str                      # COLLECTION_TITLE The title for the book being produced. This will be used for the
                                #                  filename as well as in the produced PDF.
page_list_page: str             # WIKI_BOOK_PAGE   The title of the wikipage that contains the structure of the book.
pages: list[str]                #                  List of pages from the page_list_page
_site: Site | None = None       #                  The mwclient object for the wiki
# fmt: on


def getenv_or_bail(envvar: str) -> str:
    """
    Retrieve the value of an environment variable or terminate the program if it is not set.

    Parameters
    ----------
    envvar : str
        The name of the environment variable to retrieve.

    Returns
    -------
    str
        The value of the requested environment variable.

    Raises
    ------
    SystemExit
        If the specified environment variable is not set, the program will exit.

    Notes
    -----
    This function logs a fatal error and terminates the program using `sys.exit(1)`
    if the specified environment variable is not found.

    Examples
    --------
    >>> # To use the function, ensure the environment variable is set:
    >>> # os.environ["MY_ENV_VAR"] = "my_value"
    >>> getenv_or_bail("MY_ENV_VAR")
    'my_value'
    """
    val = os.getenv(envvar)
    if val is None:
        logging.fatal("Envvar %s is not set", envvar)
        sys.exit(1)

    return val


def get_site() -> Site:
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
    global _site  # pylint: disable=global-statement
    if not _site:
        parsed = urlparse(api_url)
        scheme = parsed.scheme
        host = parsed.netloc
        path = parsed.path.removesuffix("api.php")
        session = None

        _site = Site(host, scheme=scheme, path=path)

        if verify is not None:
            session = Session()
            session.verify = verify
            _site = Site(host, scheme=scheme, path=path, pool=session)

    return _site


def get_page_list_pages() -> list[WikiPage]:
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
    page = get_site().pages[page_list_page]
    book = populate_book(page.text())
    return get_ordered_wiki_pages(book)


# Define your credentials and MediaWiki API endpoint
api_url = getenv_or_bail("WIKI_API_URL")
username = os.getenv("WIKI_USER")
password = os.getenv("WIKI_PASS")
verify = os.getenv("WIKI_CA_CERT")
title = getenv_or_bail("COLLECTION_TITLE")
page_list_page = getenv_or_bail("WIKI_BOOK_PAGE")
pages = [page.link.url for page in get_page_list_pages()]
