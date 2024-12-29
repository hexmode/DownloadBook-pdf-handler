"""Class to capture the collection mechanics."""

import asyncio
import logging
import os
import re
import tempfile
from io import BytesIO
from shutil import rmtree

import httpx
from bs4 import BeautifulSoup
from pikepdf import Dictionary, Name, Object
from pikepdf import Page as PdfPage
from pikepdf import Pdf
from pikepdf import open as pdf_open
from pikepdf._core import PageList
from playwright.async_api import Page as BrowserPage
from playwright.async_api import async_playwright

import src.settings as setting
from src.common import Common
from src.toc import TableOfContents, TocEntry


class Collection:
    """
    A class to represent a collection of wiki pages and operations to generate PDFs from them.

    Parameters
    ----------
    title : str
        The title for this collection.
    output_file : str
        The file path where the generated PDF will be saved.
    page_list : list[str]
        A list of URLs.

    Attributes
    ----------
    title : str
        The title for this collection.
    page_list : list[str]
        A list of URLs that make up the subsequent pages of the book.
    title_list : list[TocEntry]
        A list of Titles in the collection
    page_num : int
        Internal use for current page count.
    output_list : list[str]
        A list of output files.
    output_file : str
        The file path where the generated PDF will be saved.
    url_to_page : dict[str, int]
        Mapping of urls to pages
    """

    title: str
    page_list: list[setting.TocOffset]
    title_list: list[TocEntry]
    page_num: int
    output_list: list[str]
    output_file: str
    url_to_page: dict[str, int]
    logger: logging.Logger

    def __init__(
            self, title: str, output_file: str, page_list: list[setting.TocOffset], logger: logging.Logger
    ) -> None:
        """
        Initialize the collection.

        Parameters
        ----------
        title : str
            The title for this collection.
        output_file : str
            The file path where the generated PDF will be saved.
        page_list : list[str]
            A list of URLs.
        """
        self.title = title
        self.page_list = page_list
        self.title_list = []
        self.output_list = []
        self.url_to_page = {}
        self.output_file = output_file
        self.page_num = 1
        self.logger = logger

    def create_pdf(self) -> str:
        """
        Create a PDF by combining rendered pages.

        Iterates through the page list, sanitizing page urls, rendering
        individual PDF files, and then merges them into a single PDF file.

        Returns
        -------
        str
            The path to the combined PDF output file.
        """
        build_dir = tempfile.mkdtemp()
        for page in self.page_list:
            sanitized_page = re.sub(r'[\/:*?"<>|]', "_", page.title)
            output = build_dir + "/" + sanitized_page

            self.logger.debug("Saving %s to %s.", sanitized_page, output)
            asyncio.run(self.render_pdf(page.title, output, page.level))

        for title in self.title_list:
            self.logger.info(title)
        self.concat_pages()
        rmtree(build_dir)
        return self.output_file

    def concat_pages(self) -> None:
        """
        Concatenate PDF pages from a list of file paths into a single PDF.

        Insert a Table of Contents as the first page.
        """
        with Pdf.new() as pdf_writer:
            page_offset = 1

            for pdf_path in self.output_list:
                with Pdf.open(pdf_path) as pdf_reader:
                    pages = pdf_reader.pages
                    self.logger.debug("Adding %d page(s) from %s to %s.", len(pages), pdf_path, self.output_file)
                    self.add_pages(pages, pdf_writer, page_offset)
                    page_offset += len(pages)

            toc = TableOfContents(pdf_writer, self.title_list)
            toc_pages = toc.generate_toc_pdf()
            page = 1
            for toc_page in toc_pages:
                self.ensure_resources(toc_page)
                self.add_footer(Common.int_to_roman(page), toc_page)
                pdf_writer.pages.insert(page - 1, toc_page)
                page += 1

            try:
                pdf_writer.save(self.output_file)
            except OSError:
                self.logger.fatal(
                    f"OSError when trying to save. Does the name contain bad characters? {self.output_file}"
                )

    def add_pages(self, pages: PageList, writer: Pdf, start_page: int) -> None:
        """
        Add pages to a PDF writer with text in the heading and footer.

        Parameters
        ----------
        pages : PageList
            A list of pages to be added to the writer.
        writer : Pdf
            The PDF writer object where pages will be appended.
        start_page : int
            The starting page number to add to the footer text.
        """
        page_number = start_page
        for page in pages:
            self.ensure_resources(page)
            self.add_header(self.title, page)
            self.add_footer(f"Page {page_number}", page)
            self.replace_links_in_page(page)

            writer.pages.append(page)
            page_number += 1

    def ensure_resources(self, page: PdfPage) -> None:
        """
        Ensure that the resources dictionary for the page defines the /F1 font.

        Parameters
        ----------
        page : PdfPage
            The PDF page to check or update the resources.
        """
        font_dict = Common.font_dictionary()

        page.add_resource(font_dict, Name.Font, Name(Common.HF_FONT_SIGN))

    def add_header(self, header: str, page: PdfPage) -> PdfPage:
        """
        Add a header to the specified PDF page.

        Parameters
        ----------
        header : str
            The header text to add.
        page : PdfPage
            The PDF page where the header will be added.

        Returns
        -------
        PdfPage
            The PDF page with the header added.
        """
        encoded = Common.header(header)
        page.contents_add(encoded, prepend=True)
        return page

    def add_footer(self, footer: str, page: PdfPage) -> PdfPage:
        """
        Add a header to the specified PDF page.

        Parameters
        ----------
        footer : str
            The footer text to add.
        page : PdfPage
            The PDF page where the header will be added.

        Returns
        -------
        PdfPage
            The PDF page with the footer added.
        """
        encoded = Common.footer(footer)
        page.contents_add(encoded, prepend=True)
        return page

    def fetch_html(self, url: str) -> str:
        """
        Fetch the HTML content from the specified URL.

        Parameters
        ----------
        url : str
            The URL to fetch the HTML content from.

        Returns
        -------
        str
            The HTML content of the specified URL.
        """
        with httpx.Client(timeout=30, verify=setting.verify if setting.verify is not None else True) as client:
            response = client.get(url)
            response.raise_for_status()  # Raise an error for non-2xx responses
            return response.text

    async def render_pdf(self, url: str, output_file: str, level: int) -> None:
        """
        Generate a PDF from a given URL and save it to the specified output file.

        Parameters
        ----------
        url : str
            The URL of the webpage to be rendered into a PDF.
        output_file : str
            The file path where the generated PDF will be saved.
        level : int
            The level of indention this should get in the ToC.
        """
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page()

            self.logger.info("Rendering url: %s to %s", url, output_file)

            page_content = self.fetch_html(url)
            title = self.extract_text_with_xslt(page_content, "h1#firstHeading")
            if title is None:
                title = "Untitled"  # Shouldn't happen with MediaWiki
            self.title_list.append(TocEntry(url=url, title=title, page=self.page_num, level=level))
            self.url_to_page[url] = self.page_num + 1

            self.output_list.append(output_file)

            await page.goto(url)

            await self.output_page(page, output_file)
            await browser.close()

    def extract_text_with_xslt(self, html: str, xslt_selector: str) -> str | None:
        """
        Extract text from HTML content using an XSLT selector.

        Parameters
        ----------
        html : str
            The HTML content as a string.
        xslt_selector : str
            The XSLT selector to apply for extracting text.

        Returns
        -------
        str or None
            Extracted text if found, otherwise None.
        """
        soup = BeautifulSoup(html, "html.parser")
        result = soup.select(xslt_selector)
        if result:
            if hasattr(result[0], "text"):
                return result[0].text
        return None

    async def output_page(self, page: BrowserPage, output_file: str) -> None:
        """
        Produce a single page.

        Parameters
        ----------
        page : BrowserPage
            The page object to produce and render.
        output_file : str
            The path to the output file where the page will be saved.
        """
        rendered = await page.pdf(outline=True, format="Letter")
        if rendered is None:
            self.logger.info("No pages")
            return

        with pdf_open(BytesIO(rendered)) as pdf:
            page_count = len(pdf.pages)
            self.logger.info("Produced %d page(s) starting on %s", page_count, self.page_num)
            self.page_num += page_count

            # Ensure directories exist
            dirname = os.path.dirname(output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)

            pdf.save(output_file)

    def replace_links_in_page(self, page: PdfPage) -> None:
        """
        Replace links to the wiki URL with links to the corresponding PDF page numbers.

        This updates any instances of a URL in the PDF content streams, replacing them with
        links pointing to internal PDF pages based on self.title_list.

        Parameters
        ----------
        page : PdfPage
            The page to replace links in.
        """
        if "/Annots" not in page:
            return
        for annot in page["/Annots"]:
            subtype = annot["/Subtype"]
            a = annot.get("/A", None) if subtype == "/Link" else None
            uri = a.get("/URI", None) if a is not None else None

            if uri in self.url_to_page:
                self.replace_url_link(uri, annot)

    def replace_url_link(self, uri: str, annot_obj: Object) -> None:
        """
        Replace a URI with an internal link if it matches an entry in `url_to_page`.

        This function modifies the provided `annot_obj` so that it points to an
        internal destination in the document instead of an external URI. The
        internal destination is determined based on the `url_to_page` mapping.

        Parameters
        ----------
        uri : str
            The URI to be replaced if it exists in the `url_to_page` dictionary.
        annot_obj : dict
            The annotation object representing the link. This object will be
            modified in-place to include a GoTo action that points to an internal
            destination in the document.
        """
        self.logger.info("Fixing link: %s -> page %s", uri, self.url_to_page[uri])
        annot_obj["/A"] = Dictionary(
            {
                "/S": Name("/GoTo"),  # GoTo action instead of URI
                "/D": [self.url_to_page[uri], Name("/Fit")],  # Link to the destination page
            }
        )
