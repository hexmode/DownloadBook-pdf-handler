"""Class to represent a chapter."""

from downloadbook_pdf_handler.section import Section
from downloadbook_pdf_handler.wiki_page import WikiPage


class Chapter:  # pylint: disable=too-few-public-methods
    """
    TypedDict representing a chapter in the book.

    Parameters
    ----------
    page : WikiLink
        A WikiLink object that represents a link to a specific wiki page.

    Attributes
    ----------
    title : str
        Chapter title.
    wiki_pages : WikiPage
        The top-level Wiki page
    sections : list[Section]
        Sections within the chapter.
    """

    title: str
    wiki_pages: list[WikiPage]
    sections: list[Section]

    def __init__(self, page: WikiPage):
        """
        Initialize an instance of the class with a WikiLink object.

        Parameters
        ----------
        page : WikiLink
            A WikiLink object that represents a link to a specific wiki page.
        """
        self.title = page.link.label
        self.wiki_pages = [page]
        self.sections = []

    def start_section(self, page: WikiPage) -> Section:
        """
        Start a section of a chapter.

        Parameters
        ----------
        page : WikiLink
            A WikiLink object that represents a link to a specific wiki page.

        Returns
        -------
        Section
            The section just created.
        """
        section = Section(page)
        self.sections.append(section)
        return section
