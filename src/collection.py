"""Class to capture the collection mechanics."""

import asyncio
import logging
import os
from io import BytesIO
from shutil import rmtree
import tempfile
import re

from lxml import etree
import httpx
from playwright.async_api import async_playwright, Page
import pikepdf

from src.toc import TableOfContents, TocEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Collection:
    """
    A class to represent a collection of web pages and operations to generate and modify PDFs.

    Attributes
    ----------
    page_list : list of str
        A list of URLs that make up the subsequent pages of the book.
    page_num : int
        Internal use for current page count.
    output_file : str
        The file path where the generated PDF will be saved.
    """

    page_list: list[str]
    title_list: list[TocEntry]
    page_num: int
    output_file: str

    def __init__(self, output_file: str, page_list: list[str]) -> None:
        self.page_list = page_list
        self.title_list = []
        self.output_file = output_file
        self.page_num = 1

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
        output_list = []
        build_dir = tempfile.mkdtemp()
        for page in self.page_list:
            sanitized_page = re.sub(r'[\/:*?"<>|]', '_', page)
            output = build_dir + "/" + sanitized_page

            logger.debug("Saving %s to %s.", sanitized_page, output)
            asyncio.run(self.render_pdf(page, output))
            output_list.append(output)

        for title in self.title_list:
            logger.info(title)
        self.concat_pages(output_list)
        rmtree(build_dir)
        return self.output_file


    def concat_pages(self, output_list: list[str]) -> None:
        """
        Concatenate PDF pages from a list of file paths into a single PDF.

        Insert a Table of Contents as the first page.

        Parameters
        ----------
        output_list : list of str
            List of PDF file paths to be concatenated.

        Returns
        -------
        None

        """
        with pikepdf.Pdf.new() as pdf_writer:
            page_offset = 0

            for pdf_path in output_list:
                with pikepdf.Pdf.open(pdf_path) as pdf_reader:
                    page_offset += len(pdf_reader.pages)
                    logger.debug("Adding %d page(s) from %s to %s.", len(pdf_reader.pages), pdf_path, self.output_file)
                    pdf_writer.pages.extend(pdf_reader.pages)

            toc_page = TableOfContents(pdf_writer, self.title_list)
            pdf_writer.pages.insert(0, toc_page.generate_toc_pdf())

            pdf_writer.save(self.output_file)

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
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()  # Raise an error for non-2xx responses
            return response.text

    async def render_pdf(self, url: str, output_file: str) -> None:
        """
        Generate a PDF from a given URL and save it to the specified output file.

        Parameters
        ----------
        url : str
            The URL of the webpage to be rendered into a PDF.
        output_file : str
            The file path where the generated PDF will be saved.

        Returns
        -------
        None
            This function does not return any value.
        """
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page()

            logger.info("Rendering url: %s to %s", url, output_file)

            page_content = self.fetch_html(url)
            title = self.extract_text_with_xslt(page_content, "//h1[@id='firstHeading']")
            if title is None:
                title = "Untitled"   # Shouldn't happen with MediaWiki
            self.title_list.append(TocEntry(title=title, page=self.page_num))

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
        parser = etree.HTMLParser()
        tree = etree.fromstring(html, parser)
        result = tree.xpath(xslt_selector)
        if result:
            # If the result is an element, get its text
            if isinstance(result[0], etree._Element):
                return result[0].text
            # If the result is already a text node or string
            return result[0]
        return None

    async def output_page(self, page: Page, output_file: str) -> None:
        """
        Produce a single page.

        Parameters
        ----------
        page : Page
            The page object to produce and render.
        output_file : str
            The path to the output file where the page will be saved.
        page_num : list of int
            A list containing a single integer that tracks the cumulative page count.

        Returns
        -------
        None
            This function does not return a value.
        """
        rendered = await page.pdf(outline=True, format='Letter')
        if rendered is None:
            logger.info("No pages")
            return

        with pikepdf.open(BytesIO(rendered)) as pdf:
            page_count = len(pdf.pages)
            logger.info("Produced %d page(s) starting on %s", page_count, self.page_num)
            self.page_num += page_count

            # Ensure directories exist
            dirname = os.path.dirname(output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)

            pdf.save(output_file)

    def replace_links_in_page(self, page: pikepdf.Page, old_url: str, new_url: str) -> None:
        """
        Replace links in a PDF page from old_url to new_url.

        Parameters
        ----------
        page : pikepdf.Page
            The PDF page in which to replace links.
        old_url : str
            The URL to be replaced.
        new_url : str
            The new URL to set in place of the old URL.

        Returns
        -------
        None
        """
        annots: pikepdf.Object | None = page.get("/Annots")
        if annots is None or not isinstance(annots, pikepdf.objects.Object):
            return

        for annot in annots.as_list():
            if annot is None or not isinstance(annot, pikepdf.objects.Object):
                continue
            uri = annot.get("/A", {}).get("/URI")
            if uri and uri == old_url:
                logger.info("Updating link: %s to %s", uri, new_url)
                annot["/A"]["/URI"] = pikepdf.String(new_url)

    def modify_links(self, pdf_bytes: bytes, old_url: str, new_url: str) -> bytes | None:
        """
        Modify hyperlinks in a PDF by replacing a specified URL with a new one.

        Parameters
        ----------
        pdf_bytes : bytes
            The byte content of the PDF.
        old_url : str
            The URL to be replaced.
        new_url : str
            The new URL to replace the existing one.

        Returns
        -------
        bytes | None
            The modified PDF content as bytes if successful, otherwise None.
        """
        try:
            result_pdf: bytes
            with pikepdf.open(BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    self.replace_links_in_page(page, old_url, new_url)
                output = BytesIO()
                pdf.save(output)
                result_pdf = output.getvalue()

            return result_pdf
        except Exception as e:  # pylint: disable=W0718
            logger.error("Failed to modify links: %s", str(e))
            return None
