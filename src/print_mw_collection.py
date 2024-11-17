"""Print the collection that DocumentBook gives us."""

import asyncio
import logging

from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_pdf(url: str, output_file: str) -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()

        await page.goto(url)

        # Fetch <h1> and <h2> elements and their positions for TOC generation
        headers = await page.evaluate('''() => {
            const getHeaderInfo = (header) => ({
                type: header.tagName.toLowerCase(),
                text: header.textContent.trim(),
                top: header.getBoundingClientRect().top
            });

            return [
                ...Array.from(document.querySelectorAll('h1')).map(getHeaderInfo),
                ...Array.from(document.querySelectorAll('h2')).map(getHeaderInfo)
            ].sort((a, b) => a.top - b.top);
        }''')

        toc = []
        for header in headers:
            page_number = int(header['top'] / 800) + 1
            indent = "    " if header['type'] == 'h2' else ""
            toc.append(f"{indent}{header['text']} - Page {page_number}")

        # Print TOC for debugging purposes
        logger.info("Table of Contents:\n" + "\n".join(toc))

        await page.pdf(path=output_file, format='letter')

        await browser.close()


def main() -> None:
    url = 'https://en.wikipedia.org/w/index.php?title=Samantha_Harvey_(author)'
    output_file = 'output.pdf'
    asyncio.run(generate_pdf(url, output_file))
