"""Debugging utility."""

import logging
import os
import sys
from typing import Iterable, cast

import pikepdf
from pikepdf import Pdf

logging.basicConfig(level=logging.DEBUG)


def extract_urls(pdf_path: str) -> set[str]:
    """
    Extract URLs from a PDF document.

    This function reads the content streams of the pages in the provided PDF file
    and identifies URLs. It returns a list of all URLs found within the document.

    Parameters
    ----------
    pdf_path : str
        The path to the PDF file from which URLs will be extracted.

    Returns
    -------
    list of str
        A list containing the URLs found in the PDF.
        If no URLs are found or the PDF has no content streams, the list
        will be empty.

    Notes
    -----
    - This function assumes that URLs follow a standard format (e.g., "http://").
    - Pages without content streams will be skipped, and a message will be
      printed for informational purposes.

    Examples
    --------
    >>> extract_urls("example.pdf")
    Page 1: URLs found
    Page 2: URLs found
    ['http://example.com', 'https://anotherexample.com']
    """
    urls = set()
    with Pdf.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Access the raw content stream of the page
            if "/Annots" not in page:
                continue

            page_urls = set()
            for annot in cast(Iterable[pikepdf._core.Object], page["/Annots"]):
                subtype = annot["/Subtype"]
                a = annot.get("/A", None) if subtype == "/Link" else None
                uri = str(a.get("/URI", None)) if a is not None else None

                if uri is not None:
                    page_urls.add(uri)

            if len(page_urls) > 0:
                logging.info("Page %d: URLs %s", page_num, ", ".join(sorted(page_urls)))

            urls.update(page_urls)

    return urls


def main() -> None:
    """Execute main program."""
    pdf_path = os.getenv("COLLECTION_TITLE")
    if pdf_path is None:
        logging.critical("COLLECTION_TITLE envvar isn't set!")
        sys.exit(1)
    urls = sorted(extract_urls(pdf_path.replace(" ", "_") + ".pdf"))
    logging.info("Extracted URLs: %s", urls)
