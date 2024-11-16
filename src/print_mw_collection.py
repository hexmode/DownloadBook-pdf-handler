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

        # Fetch all <h1> elements and their positions for TOC generation
        h1_positions = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('h1')).map(h1 => ({
                text: h1.textContent.trim(),
                top: h1.getBoundingClientRect().top
            }));
        }''')

        # Calculate page numbers and generate a TOC
        toc = []
        for h1 in h1_positions:
            # Assuming 800px per page for this example
            page_number = int(h1['top'] / 800) + 1
            toc.append(f"{h1['text']} - Page {page_number}")

        # Print TOC for debugging purposes
        logger.info("\n".join(toc))

        await page.pdf(path=output_file, format='A4')

        await browser.close()


def main() -> None:
    url = 'https://en.wikipedia.org/w/index.php?title=Samantha_Harvey_(author)'
    output_file = 'output.pdf'
    asyncio.run(generate_pdf(url, output_file))
