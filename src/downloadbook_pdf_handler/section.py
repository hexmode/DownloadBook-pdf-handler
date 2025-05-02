"""Class to represent a Section."""

from downloadbook_pdf_handler.wiki_page import WikiPage


class Section:  # pylint: disable=too-few-public-methods
    """
    TypedDict representing a section within a chapter.

    Parameters
    ----------
    page : WikiPage
        A WikiPage object.

    Attributes
    ----------
    title : str
        Section title.
    wiki_pages : list[WikiPage]
        List of wiki pages in the section.
    """

    title: str
    wiki_pages: list[WikiPage]

    def __init__(self, page: WikiPage):
        """
        Initialize an instance of the class with a WikiLink object.

        Parameters
        ----------
        page : WikiPage
            A WikiPage object.
        """
        self.title = page.link.label
        self.wiki_pages = [page]

    def add_page(self, page: WikiPage) -> None:
        """
        Add a new WikiPage to the wiki_pages list.

        Parameters
        ----------
        page : WikiPage
            The WikiPage object to be added to the list.
        """
        self.wiki_pages.append(page)
