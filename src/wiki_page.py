"""Class to represent a page."""

from src.wiki_link import WikiLink


class WikiPage:  # pylint: disable=too-few-public-methods
    """
    Class representing a wiki page.

    Parameters
    ----------
    link : WikiLink
        A WikiLink object that represents a link to a specific wiki page.
    level : int
        The Table of Contents level.

    Attributes
    ----------
    link : WikiLink
        The wiki link for this page.
    level : int
        The Table of Contents level.
    content : str
        Content of the wiki page (raw/rendered text or markdown).
    rendered_pages : list[int]
        Number(s) of the resulting PDF pages (filled after rendering).
    """

    link: WikiLink
    level: int
    content: str | None = None
    rendered_pages: list[int] = []

    def __init__(self, link: WikiLink, level: int):
        """
        Initialize an instance of the class with a WikiLink object.

        Parameters
        ----------
        link : WikiLink
            A WikiLink object that represents a link to a specific wiki page.
        level : int
            The Table of Contents level.
        """
        self.link = link
        self.level = level
