"""Table of Contents."""

import logging
from collections import namedtuple
from textwrap import dedent

from pikepdf import Array, Dictionary, Name, Object
from pikepdf import Page as PdfPage
from pikepdf import Pdf, Rectangle, Stream

from src.common import Common

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TocEntry = namedtuple("TocEntry", ["title", "page", "level"])
TOC_FONT_SIGN = "/F1"
TOC_FONT_SIZE = 12


class PdfTocEntry:
    """
    Represent a PDF Table of Contents (TOC) entry.

    Parameters
    ----------
    pdf : Pdf
        The PDF object for which the TOC entry is created.
    entry : TocEntry
        The TOC entry specifying title, page, etc.
    offset : int
        The vertical offset for the TOC entry in the PDF.

    Attributes
    ----------
    pdf : Pdf
        The PDF object associated with this TOC entry.
    offset : int
        The vertical offset in the PDF for this TOC entry.
    content : bytes
        The textual content of the TOC entry in PDF format.
    annot : Object
        The annotation object for the TOC entry.
    """

    pdf: Pdf
    offset: int
    content: bytes
    annot: Object

    def __init__(self, pdf: Pdf, entry: TocEntry, offset: int) -> None:
        """
        Initialize the PdfTocEntry with the PDF object, TOC entry content, and its offset.

        Parameters
        ----------
        pdf : Pdf
            The PDF object for which the TOC entry is created.
        entry : TocEntry
            The TOC entry specifying title, page, etc.
        offset : int
            The vertical offset for the TOC entry in the PDF.
        """
        self.pdf = pdf
        self.offset = offset
        self.content = self.get_content(entry)
        self.annot = self.get_annot(entry)

    def escape_pdf_text(self, value: str) -> str:
        """
        Escape PDF-specific characters in a given string.

        Parameters
        ----------
        value : str
            The string to escape.

        Returns
        -------
        str
            The escaped string.
        """
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def get_content(self, entry: TocEntry) -> bytes:
        """
        Generate the PDF content for the TOC entry.

        Parameters
        ----------
        entry : TocEntry
            The TOC entry containing title and page number.

        Returns
        -------
        bytes
            The encoded PDF content for the TOC entry.
        """
        logger.debug("Making Toc content entry for %s to %d", entry.title, entry.page)
        return dedent(
            f"""q
            BT
            {TOC_FONT_SIGN} {TOC_FONT_SIZE} Tf
            {Common.ID_TRANSFORM} {Common.MARGIN} {self.offset} Tm
            ({self.escape_pdf_text(entry.title)} - {entry.page}) Tj
            ET
            Q"""
        ).encode("utf-8")

    def get_annot(self, entry: TocEntry) -> Object:
        """
        Create an annotation object for the TOC entry.

        Parameters
        ----------
        entry : TocEntry
            The TOC entry specifying title and page.

        Returns
        -------
        Object
            The annotation dictionary for the TOC entry.
        """
        return Dictionary(
            {
                "/Type": Name("/Annot"),
                "/Subtype": Name("/Link"),  # Define this as a Link annotation
                "/Rect": Rectangle(  # Clickable area
                    Common.MARGIN, self.offset - (Common.LINE_HEIGHT / 2), 300, self.offset + (Common.LINE_HEIGHT / 2)
                ),
                "/Border": [0, 0, 0],  # No visible border for the link
                "/A": Dictionary(
                    {
                        "/S": Name("/GoTo"),  # GoTo action type
                        "/D": [self.pdf.pages[entry.page - 1].obj, Name("/Fit")],  # Destination to target page
                    }
                ),
            }
        )


class TableOfContents:
    """
    A helper class to generate a Table of Contents (ToC) PDF.

    Parameters
    ----------
    pdf : Pdf
        Pikepdf object used to set up the ToC.
    title_list : list[TocEntry]
        A list of titles to be included in the Table of Contents.

    Attributes
    ----------
    title_list : list of str
        A list of titles to be included in the Table of Contents.
    """

    title_list: list[TocEntry]
    pdf: Pdf

    def __init__(self, pdf: Pdf, title_list: list[TocEntry]):
        """
        Initialize our Table of Contents.

        Parameters
        ----------
        pdf : Pdf
            Pikepdf object used to set up the ToC.
        title_list : list[TocEntry]
            A list of titles to be included in the Table of Contents.
        """
        self.pdf = pdf
        self.title_list = title_list

    def generate_single_toc_page(self, start_idx: int) -> tuple[PdfPage, int]:
        """
        Generate a table of contents PDF and return it to a caller.

        Parameters
        -----------
        start_idx : int
            The index in `title_list` to begin generating the page.

        Returns
        -------
        tuple[PdfPage, int]
            A list of PdfPage object containing the table of contents page.
        """
        # Define resources dictionary (e.g., fonts)
        resources = self.get_resources()

        # Add content stream
        toc_text = Common.header("Table of Contents", TOC_FONT_SIZE, TOC_FONT_SIGN)
        toc_annots = self.pdf.make_indirect(Array())

        # Add content stream for each title
        i = Common.PAGE_HEIGHT - Common.MARGIN * 2
        next_idx = start_idx
        while next_idx < len(self.title_list):
            entry = self.title_list[next_idx]
            toc_entry = PdfTocEntry(self.pdf, entry, i)
            toc_text += toc_entry.content
            toc_annots.append(self.pdf.make_indirect(toc_entry.annot))
            i -= Common.LINE_HEIGHT
            next_idx += 1

            # Break at the bottom of the page
            if i < Common.MARGIN * 2:
                break

        # finalize the page
        content = Stream(self.pdf, toc_text)
        page_dict = Dictionary(
            {
                "/Type": Name("/Page"),
                "/MediaBox": Array([0, 0, Common.PAGE_WIDTH, Common.PAGE_HEIGHT]),
                "/Resources": self.pdf.make_indirect(resources),
                "/Contents": self.pdf.make_indirect(content),
                "/Annots": self.pdf.make_indirect(toc_annots),
            }
        )

        # Add the page to the PDF
        page = PdfPage(self.pdf.make_indirect(page_dict))

        return page, next_idx

    def generate_toc_pdf(self) -> list[PdfPage]:
        """
        Generate a table of contents PDF and return it to a caller.

        Returns
        -------
        list[PdfPage]
            A list of PdfPage object containing the table of contents page.
        """
        toc_pages = []
        next_idx = 0

        # Generate single pages with offsets until all entries are processed
        while next_idx < len(self.title_list):
            page, next_idx = self.generate_single_toc_page(next_idx)
            toc_pages.append(page)

        return toc_pages

    def get_resources(self) -> Dictionary:
        """
        Get the resources dictionary for the PDF.

        Returns
        -------
        Dictionary
            A dictionary containing the necessary resources for the PDF, including font information.
        """
        font_ref = self.pdf.make_indirect(Common.font_dictionary("Helvetica-Bold"))

        # Create a valid resources dictionary
        return Dictionary({"/Font": Dictionary({TOC_FONT_SIGN: font_ref})})
