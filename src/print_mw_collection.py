"""Print the collection that DocumentBook gives us."""

from src.collection import Collection

URL_PREFIX = 'https://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_article/'

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
    pages = [
        'March_1,_2004',
        'March_2,_2004',
        'March_3,_2004',
        'March_4,_2004',
        'March_5,_2004',
        'March_6,_2004',
        'March_7,_2004',
        'March_8,_2004',
        'March_9,_2004',
        'March_10,_2004',
        'March_11,_2004',
        'March_12,_2004',
        'March_13,_2004',
        'March_14,_2004',
        'March_15,_2004',
        'March_16,_2004',
        'March_17,_2004',
        'March_18,_2004',
        'March_19,_2004',
        'March_20,_2004',
        'March_21,_2004',
        'March_22,_2004',
        'March_23,_2004',
        'March_24,_2004',
        'March_25,_2004',
        'March_26,_2004',
        'March_27,_2004',
        'March_28,_2004',
        'March_29,_2004',
        'March_30,_2004',
        'March_31,_2004',
    ]

    page_list = [URL_PREFIX + page for page in pages]
    Collection("March 2004 Featured Articles", "March 2004 Featured Articles.pdf", page_list).create_pdf()
