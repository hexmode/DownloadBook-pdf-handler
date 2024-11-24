"""Table of Contents."""
from collections import namedtuple
from textwrap import dedent
import logging

from pikepdf import Array, Dictionary, Name, Object, Pdf, Page, Rectangle, Stream

from src.common import Common

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
TocEntry = namedtuple('TocEntry', ['title', 'page'])
TOC_FONT_SIGN = '/F1'
TOC_FONT_SIZE = 12


class PdfTocEntry:
    """
    Represent a PDF Table of Contents (TOC) entry.

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
        logger.debug("Setting up entry: %s", type(entry))
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
        return value.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

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
        return dedent(f"""q
            BT
            {TOC_FONT_SIGN} {TOC_FONT_SIZE} Tf
            {Common.ID_TRANSFORM} {Common.MARGIN} {self.offset} Tm
            ({self.escape_pdf_text(entry.title)} - {entry.page}) Tj
            ET
            Q""").encode('utf-8')

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
        return Dictionary({
            '/Type': Name('/Annot'),
            '/Subtype': Name('/Link'),                  # Define this as a Link annotation
            '/Rect': Rectangle(                         # Clickable area
                100, self.offset - (Common.LINE_HEIGHT / 2),
                300, self.offset + (Common.LINE_HEIGHT / 2)),
            '/Border': [0, 0, 0],                       # No visible border for the link
            '/A': Dictionary({
                '/S': Name('/GoTo'),                    # GoTo action type
                '/D': [self.pdf.pages[entry.page - 1].obj, Name('/Fit')]   # Destination to target page
            })
        })


class TableOfContents:
    """
    A helper class to generate a Table of Contents (ToC) PDF.

    Attributes
    ----------
    title_list : list of str
        A list of titles to be included in the Table of Contents.

    Methods
    -------
    __init__(title_list)
        Initializes the TableOfContents with a list of titles.
    generate_toc_pdf() -> Pdf
        Generates and returns a PDF object containing the table of contents.
    """

    title_list: list[TocEntry]
    pdf: Pdf

    def __init__(self, pdf: Pdf, title_list: list[TocEntry]):
        """
        Initialize our Table of Contents.

        Parameters
        ----------
        title_list : list[TocEntry]
            A list of titles to be included in the Table of Contents.
        """
        self.pdf = pdf
        self.title_list = title_list

    def generate_toc_pdf(self) -> Page:
        """
        Generate a table of contents PDF and return it to a caller.

        Returns
        -------
        Page
            A Page object containing the table of contents page.
        """
        # Define resources dictionary (e.g., fonts)
        resources = self.get_resources()

        # Add content stream
        toc_text = Common.header("Table of Contents", TOC_FONT_SIZE, TOC_FONT_SIGN)
        toc_annots = self.pdf.make_indirect(Array())

        # Add content stream for each title
        i = Common.PAGE_HEIGHT - Common.MARGIN
        for entry in self.title_list:
            toc_entry = PdfTocEntry(self.pdf, entry, i)
            toc_text += toc_entry.content
            toc_annots.append(self.pdf.make_indirect(toc_entry.annot))
            i -= Common.LINE_HEIGHT

        content = Stream(self.pdf, toc_text)

        page_dict = Dictionary({
            '/Type': Name('/Page'),
            '/MediaBox': Array([0, 0, Common.PAGE_WIDTH, Common.PAGE_HEIGHT]),
            '/Resources': self.pdf.make_indirect(resources),
            '/Contents': self.pdf.make_indirect(content),
            '/Annots': self.pdf.make_indirect(toc_annots)
        })

        # Add the page to the PDF
        return Page(self.pdf.make_indirect(page_dict))

    def get_resources(self) -> Dictionary:
        """
        Get the resources dictionary for the PDF.

        Returns
        -------
        Dictionary
            A dictionary containing the necessary resources for the PDF, including font information.
        """
        font_ref = self.pdf.make_indirect(Common.font_dictionary('Helvetica-Bold'))

        # Create a valid resources dictionary
        return Dictionary({
            '/Font': Dictionary({TOC_FONT_SIGN: font_ref})
        })
