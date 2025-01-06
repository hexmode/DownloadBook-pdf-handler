"""Describe the structure of the document."""

# pylint: disable=unsubscriptable-object

from src.book import Book
from src.chapter import Chapter
from src.exceptions import NoChapterForSectionError, NoLinkFoundError, ParseError
from src.section import Section
from src.wiki_link import WikiLink
from src.wiki_page import WikiPage


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
    if start == 1 and end == -1:
        raise NoLinkFoundError(line)

    bits = line[start:end].split("|", 1)
    link = label = "Main_page"
    if len(bits) == 2:
        link, label = bits
    if len(bits) == 1:
        link = label = bits[0]
    if len(bits) != 1 and len(bits) != 2:
        raise ParseError(f"The line '{line}' could not be parsed.")
    return WikiLink(link, label)


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
