"""Describe the structure of the document."""

# pylint: disable=unsubscriptable-object


class WikiLink:  # pylint: disable=too-few-public-methods
    """
    A named tuple representing a hyperlink and its associated label.

    Parameters
    ----------
    link : str
        The hyperlink represented as a string.
    label : str
        The label or text associated with the hyperlink.

    Attributes
    ----------
    link : str
        The hyperlink represented as a string.
    label : str
        The label or text associated with the hyperlink.
    """

    url: str
    label: str

    def __init__(self, link: str, label: str):
        """
        Create a WikiLink.

        Parameters
        ----------
        link : str
            The hyperlink represented as a string.
        label : str
            The label or text associated with the hyperlink.
        """
        self.url = link
        self.label = label


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


def parse_line(line: str) -> WikiLink:
    """
    Parse a MediaWiki-style link and extract its URL (link) and label (title).

    Parameters
    ----------
    line : str
        A string containing a MediaWiki-style link. The link should be in the format
        `[[path/to/page|Page Title]]`.

    Returns
    -------
    WikiLink
        An object containing the extracted URL (link) and label (title).

    Examples
    --------
    >>> parse_line("[[path/to/page|Page Title]]")
    WikiLink(link="path/to/page", label="Page Title")
    """
    start = line.find("[[") + 2
    end = line.find("]]")
    link, label = line[start:end].split("|", 1)
    return WikiLink(link, label)


class NoChapterForSectionError(Exception):
    """Exception thrown if there is no chapter started yet."""


def populate_book(raw_structure: str) -> Book:
    """
    Parse the hierarchical MediaWiki-style structure and generate a Book object.

    Parameters
    ----------
    raw_structure : str
        A string representing the hierarchical MediaWiki-style structure of a book.
        This structure includes lines representing chapters, sections, and potentially
        nested subsections, formatted with specific prefixes to indicate hierarchy levels:
        - Chapters are represented by lines starting with "* ".
        - Sections are represented by lines starting with ":* ".
        - Subsections are represented by lines starting with "::* ".

    Returns
    -------
    Book
        A structured representation of the book in the form of a `Book` object. This object contains:
        - "title": The title of the book.
        - "chapters": A list of chapters, where each chapter contains:
            - "wiki_page": A wiki page directly under the chapter
                - "title": The title of the wiki page.
                - "link": The link associated with the wiki page.
            - "sections": A list of sections within the chapter, where each section contains:
                - "title": The section title.
                - "wiki_pages": A list of nested wiki pages (subsections) within the section, where each wiki page
                  contains:
                    - "title": The title of the wiki page.
                    - "link": The link associated with the wiki page.

    Notes
    -----
    - The function assumes that the first line of `raw_structure` contains the book title.
    - Subsequent lines define the hierarchical structure of the book, with chapters, sections,
      and subsections indicated by their respective prefixes.
    - The book structure is parsed and organized into a `Book` object, which is a nested dictionary.

    Examples
    --------
    >>> raw_structure = '''
    ... * [[Book_Title|Book Title]]
    ... * [[Chapter_1_Link|Chapter 1]]
    ... :* [[Section_1_1_Link|Section 1.1]]
    ... ::* [[Subsection_1_1_1_Link|Subsection 1.1.1]]
    ... * [[Chapter_2_Link|Chapter 2]]
    ... '''
    >>> populate_book(raw_structure)
    {
        "title": "Book Title",
        "chapters": [
            {
                "title": "Chapter 1",
                "wiki_page": {"title": "Chapter 1", "link": "Chapter_1_Link"},
                "sections": [
                    {
                        "title": "Section 1.1",
                        "wiki_pages": [
                            {"title": "Subsection 1.1.1", "link": "Subsection_1_1_1_Link"}
                        ]
                    }
                ]
            },
            {
                "title": "Chapter 2",
                "wiki_page": {"title": "Chapter 2", "link": "Chapter_2_Link"},
                "sections": []
            }
        ]
    }
    """
    lines = raw_structure.strip().split("\n")
    book_link = parse_line(lines[0].strip())
    book = Book(book_link)
    current_chapter: Chapter | None = None
    current_section: Section | None = None

    for line in lines[1:]:
        line = line.strip()

        if line.startswith("* "):  # Chapter-level
            wikilink = parse_line(line[2:])
            if current_chapter:
                book.chapters.append(current_chapter)

            current_chapter = Chapter(WikiPage(wikilink, 1))

        if line.startswith(":* "):  # Section-level
            wikipage = WikiPage(parse_line(line[3:]), 2)
            if not current_chapter:
                raise NoChapterForSectionError(wikipage)

            current_section = current_chapter.start_section(wikipage)

        elif line.startswith("::* "):  # WikiPage-level
            wikilink = parse_line(line[4:])
            wiki_page = WikiPage(wikilink, 2)
            if current_section:
                current_section.wiki_pages.append(wiki_page)
            elif current_chapter:
                current_chapter.wiki_pages.append(wiki_page)

    if current_chapter:
        book.chapters.append(current_chapter)

    return book


def get_ordered_wiki_pages(book: Book) -> list[WikiPage]:
    """
    Extract a flat, ordered list of wiki pages from a Book object.

    Parameters
    ----------
    book : Book
        The result of the `populate_book` function, representing the hierarchical
        structure of a book with chapters, sections, and wiki pages.

    Returns
    -------
    List[WikiPage]
        A flat, ordered list of all wiki pages in the book, preserving their order
        as defined in the hierarchical structure.

    Examples
    --------
    >>> book = {
    ...     "title": "Book Title",
    ...     "chapters": [
    ...         {
    ...             "title": "Chapter 1",
    ...             "sections": [
    ...                 {
    ...                     "title": "Section 1.1",
    ...                     "wiki_pages": [
    ...                         {"title": "Subsection 1.1.1", "link": "Subsection_1_1_1_Link"}
    ...                     ]
    ...                 }
    ...             ],
    ...             "wiki_pages": [
    ...                 {"title": "Chapter Overview", "link": "Chapter_1_Overview_Link"}
    ...             ]
    ...         },
    ...         {
    ...             "title": "Chapter 2",
    ...             "sections": [],
    ...             "wiki_pages": [{"title": "Chapter 2 Intro", "link": "Chapter_2_Intro_Link"}]
    ...         }
    ...     ]
    ... }
    >>> get_ordered_wiki_pages(book)
    [
        {"title": "Chapter Overview", "link": "Chapter_1_Overview_Link"},
        {"title": "Subsection 1.1.1", "link": "Subsection_1_1_1_Link"},
        {"title": "Chapter 2 Intro", "link": "Chapter_2_Intro_Link"}
    ]
    """
    wiki_pages = []
    if book.front_matter is not None:
        wiki_pages.extend(book.front_matter)

    # Traverse the chapters in the book
    for chapter in book.chapters:
        # Add chapter-wide wiki pages first
        wiki_pages.extend(chapter.wiki_pages)

        # Traverse sections in the chapter
        for section in chapter.sections:
            # Add section-specific wiki pages
            wiki_pages.extend(section.wiki_pages)

    return wiki_pages
