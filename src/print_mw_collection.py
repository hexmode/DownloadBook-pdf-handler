"""Print the collection that DocumentBook gives us."""

import src.settings as setting
from src.collection import Collection


def main() -> None:
    """
    Generate PDFs for a list of wiki pages.

    This function iterates through a predefined list of wiki pages, constructs full URLs
    by appending each page name to a fixed prefix, and calls an asynchronous function to
    generate a PDF for each page.

    Raises
    ------
    Any exceptions raised within `generate_pdf` are propagated by `asyncio.run`.

    Notes
    -----
    This function uses `asyncio.run` to execute an asynchronous function `generate_pdf`,
    assuming `generate_pdf` handles the actual process of fetching the page and creating
    the PDF.

    Examples
    --------
    >>> main()
    This will generate PDF files for each page in the `pages` list.
    """
    page_list = [page.page.link for page in setting.get_page_list_pages()]
    Collection(setting.title, setting.title.replace(" ", "_") + ".pdf", page_list).create_pdf()
