"""Print the collection that DocumentBook gives us."""

from src.collection import Collection
import src.settings as setting

def main() -> None:
    """
    Generate PDFs for a list of wiki pages.

    This function iterates through a predefined list of wiki pages, constructs full URLs
    by appending each page name to a fixed prefix, and calls an asynchronous function to
    generate a PDF for each page.

    Notes
    -----
    This function uses `asyncio.run` to execute an asynchronous function `generate_pdf`,
    assuming `generate_pdf` handles the actual process of fetching the page and creating
    the PDF.

    Raises
    ------
    Any exceptions raised within `generate_pdf` are propagated by `asyncio.run`.

    Examples
    --------
    >>> main()
    This will generate PDF files for each page in the `pages` list.
    """

    page_list = [setting.URL_PREFIX + page for page in setting.pages]
    Collection(setting.title, setting.title.replace(' ', '_') + ".pdf", page_list).create_pdf()
