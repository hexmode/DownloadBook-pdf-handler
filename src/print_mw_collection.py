"""Print the collection that DocumentBook gives us."""

import logging

from src.collection import Collection
from src.settings import MissingSettingError, Settings, TocOffset


def main(logger: logging.Logger | None = None, setting: Settings | None = None) -> str:
    """
    Generate PDFs for a list of wiki pages.

    This function iterates through a predefined list of wiki pages, constructs full URLs
    by appending each page name to a fixed prefix, and calls an asynchronous function to
    generate a PDF for each page.

    Parameters
    ----------
    logger : logging.Logger | None
        The logger object if passed in.
    setting : Settings | None
        Settings object, if passed in.

    Returns
    -------
    str
        The path of the generated PDF.

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
    if logger is None:
        logger = logging.getLogger("PrintMWCollection")

    if setting is None:
        setting = Settings()

    url_prefix = setting.url_prefix
    if url_prefix is None or url_prefix == "":
        raise MissingSettingError("url_prefix")

    title = setting.collection_title
    if title is None:
        raise MissingSettingError("title")

    page_list = [TocOffset(title=url_prefix + page.title, level=page.level) for page in setting.get_pages()]
    file_name = title.replace(" ", "_") + ".pdf"
    Collection(title, file_name, page_list, logger, setting).create_pdf()
    return file_name
