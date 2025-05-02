"""Class for a Book."""

from downloadbook_pdf_handler.chapter import Chapter
from downloadbook_pdf_handler.wiki_link import WikiLink
from downloadbook_pdf_handler.wiki_page import WikiPage


class Book:  # pylint: disable=too-few-public-methods
    """
    TypedDict representing a book.

    Parameters
    ----------
    link : WikiLink
        The link that provides the title and an introduction to the book.

    Attributes
    ----------
    title : str
        Book title.
    front_matter : list[WikiPage] | None
        Wiki pages in the front matter.
    chapters : list[Chapter]
        Chapters in the book.
    """

    title: str
    front_matter: list[WikiPage] | None
    chapters: list[Chapter]

    def __init__(self, link: WikiLink):
        """
        Initialize a book.

        Parameters
        ----------
        link : WikiLink
            The link that provides the title and an introduction to the book.
        """
        self.link = link
        self.front_matter = [WikiPage(link, 1)]
        self.title = link.label
        self.chapters = []
