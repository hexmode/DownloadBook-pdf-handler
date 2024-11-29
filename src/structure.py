"""Describe the structure of the document."""
# pylint: disable=unsubscriptable-object
from typing import TypedDict, NamedTuple


class WikiLink(NamedTuple):
    """
    A named tuple representing a hyperlink and its associated label.

    Attributes
    ----------
    link : str
        The hyperlink represented as a string.
    label : str
        The label or text associated with the hyperlink.
    """

    link: str
    label: str


class WikiPage(TypedDict):
    """
    TypedDict representing a wiki page.

    Attributes
    ----------
    page : WikiLink
        The wiki link for this page.
    content : str
        Content of the wiki page (raw/rendered text or markdown).
    rendered_pages : list[int]
        Number(s) of the resulting PDF pages (filled after rendering).
    """

    page: WikiLink
    content: str
    rendered_pages: list[int]


class Section(TypedDict):
    """
    TypedDict representing a section within a chapter.

    Attributes
    ----------
    title : str
        Section title.
    wiki_pages : list[WikiPage]
        List of wiki pages in the section.
    """

    title: str
    wiki_pages: list[WikiPage]


class Chapter(TypedDict):
    """
    TypedDict representing a chapter in the book.

    Attributes
    ----------
    title : str
        Chapter title.
    sections : list[Section]
        Sections within the chapter.
    wiki_pages : list[WikiPage]
        Wiki pages directly in the chapter (not nested in sections).
    """

    title: str
    sections: list[Section]
    wiki_pages: list[WikiPage]


class Book(TypedDict):
    """
    TypedDict representing a book.

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


def populate_book(raw_structure: str) -> Book:
    """Parse the hierarchical MediaWiki-style structure and generate a Book object.

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
            - "title": The chapter title.
            - "sections": A list of sections within the chapter, where each section contains:
                - "title": The section title.
                - "wiki_pages": A list of nested wiki pages (subsections) within the section, where each wiki page
                  contains:
                    - "title": The title of the wiki page.
                    - "link": The link associated with the wiki page.
            - "wiki_pages": A list of wiki pages directly under the chapter, where each wiki page contains:
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
                "sections": [
                    {
                        "title": "Section 1.1",
                        "wiki_pages": [
                            {"title": "Subsection 1.1.1", "link": "Subsection_1_1_1_Link"}
                        ]
                    }
                ],
                "wiki_pages": [{"title": "Chapter 1", "link": "Chapter_1_Link"}]
            },
            {
                "title": "Chapter 2",
                "sections": [],
                "wiki_pages": [{"title": "Chapter 2", "link": "Chapter_2_Link"}]
            }
        ]
    }

    """
    lines = raw_structure.strip().split("\n")
    book_link = parse_line(lines[0].strip())
    book: Book = {"title": book_link.label, "front_matter": None, "chapters": []}

    current_chapter: Chapter | None = None
    current_section: Section | None = None

    for line in lines[1:]:
        line = line.strip()

        if line.startswith("* "):  # Chapter-level
            wikilink = parse_line(line[2:])
            if current_chapter:
                book["chapters"].append(current_chapter)

            current_chapter = {"title": wikilink.label, "sections": [], "wiki_pages": []}
            current_section = None

        elif line.startswith(":* "):  # Section-level
            wikilink = parse_line(line[3:])
            if current_chapter:
                current_section = {"title": wikilink.label, "wiki_pages": []}
                current_chapter["sections"].append(current_section)

        elif line.startswith("::* "):  # WikiPage-level
            wikilink = parse_line(line[4:])
            wiki_page: WikiPage = {"page": wikilink, "content": "", "rendered_pages": []}
            if current_section:
                current_section["wiki_pages"].append(wiki_page)
            elif current_chapter:
                current_chapter["wiki_pages"].append(wiki_page)

    if current_chapter:
        book["chapters"].append(current_chapter)

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

    # Traverse the chapters in the book
    for chapter in book["chapters"]:
        # Add chapter-wide wiki pages first
        wiki_pages.extend(chapter["wiki_pages"])

        # Traverse sections in the chapter
        for section in chapter["sections"]:
            # Add section-specific wiki pages
            wiki_pages.extend(section["wiki_pages"])

    return wiki_pages
