"""Debugging utility."""

import logging
import os
import re
import sys

from pikepdf import Array, Pdf, Stream

logging.basicConfig(level=logging.DEBUG)


def extract_font_sizes(pdf_path: str) -> set[float]:
    """
    Extract the font sizes used in a PDF document.

    This function reads the content streams of the pages in the provided PDF file
    and identifies font size specifications (e.g., "/F1 12 Tf"). It returns a list
    of all font sizes found within the document.

    Parameters
    ----------
    pdf_path : str
        The path to the PDF file from which font sizes will be extracted.

    Returns
    -------
    list of float
        A list containing the font sizes (as floats) encountered in the PDF.
        If no font sizes are found or the PDF has no content streams, the list
        will be empty.

    Notes
    -----
    - This function assumes that the PDF's content stream commands follow the
      standard convention for specifying font sizes (e.g., "/F1 12 Tf").
    - Pages without content streams will be skipped, and a message will be
      printed for informational purposes.

    Examples
    --------
    >>> extract_font_sizes("example.pdf")
    Page 1: Font size 12.0
    Page 2: Font size 10.5
    [12.0, 10.5]
    """
    font_sizes = set()
    with Pdf.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Access the raw content stream of the page
            if "/Contents" not in page:
                logging.info("Page %d: No content stream.", page_num)
                continue

            # `/Contents` can be a single stream or an array of streams
            contents = page["/Contents"]

            # Combine and decode content streams
            if isinstance(contents, Stream):
                content_stream = contents.read_bytes().decode("latin1")
            elif isinstance(contents, Array):
                content_stream = b"".join(c.read_bytes() for c in contents).decode("latin1")
            else:
                logging.info("Page %d: Unexpected /Contents type.", page_num)
                continue

            # Search for font setting commands like "/F1 12 Tf"
            matches = re.findall(r"\/[A-Za-z0-9]+\s+(\d+(\.\d+)?)\s+Tf", content_stream)
            page_font_sizes = set()
            for match in matches:
                page_font_sizes.add(float(match[0]))
            logging.info("Page %d: Font size %s", page_num, ", ".join(str(size) for size in sorted(page_font_sizes)))

            font_sizes.update(page_font_sizes)

    return font_sizes


def main() -> None:
    """Execute main program."""
    pdf_path = os.getenv("COLLECTION_TITLE")
    if pdf_path is None:
        logging.critical("COLLECTION_TITLE envvar isn't set!")
        sys.exit(1)
    font_sizes = sorted(extract_font_sizes(pdf_path.replace(" ", "_") + ".pdf"))
    logging.info("Extracted font sizes: %s", font_sizes)
