"""Table of Contents."""

from pikepdf import Array, Dictionary, Name, Pdf, Page, Stream


class TableOfContents:
    """
    A helper class to generate a Table of Contents (ToC) PDF.

    Attributes
    ----------
    title_list : list of str
        A list of titles to be included in the Table of Contents.

    Methods
    -------
    __init__(title_list)
        Initializes the TableOfContents with a list of titles.
    generate_toc_pdf() -> Pdf
        Generates and returns a PDF object containing the table of contents.
    """

    title_list: list[str]
    pdf: Pdf

    def __init__(self, pdf: Pdf, title_list: list[str]):
        """
        Initialize our Table of Contents.

        Parameters
        ----------
        title_list : list[str]
            A list of titles to be included in the Table of Contents.
        """
        self.pdf = pdf
        self.title_list = title_list

    def generate_toc_pdf(self) -> Page:
        """
        Generate a table of contents PDF and return it to a caller.

        Returns
        -------
        Page
            A Page object containing the table of contents page.
        """
        page_width, page_height = 612, 792  # 8.5x11 inches

        # Define resources dictionary (e.g., fonts)
        font_ref = self.pdf.make_indirect(Dictionary({
            '/Type': Name('/Font'),
            '/Subtype': Name('/Type1'),
            '/BaseFont': Name('/Helvetica-Bold'),
        }))

        # Create a valid resources dictionary
        resources = Dictionary({
            '/Font': Dictionary({'/F1': font_ref})
        })

        # Add content stream
        toc_text = b"""
            BT
            /F1 16 Tf
            1 0 0 1 100 750 Tm
            (Table of Contents) Tj
            ET
            """

        # Add content stream for each title
        for i, title in enumerate(self.title_list):
            title_y_position = 730 - (i * 20)  # Adjust y-position for each title
            toc_text += f"""
                BT
                /F1 12 Tf
                1 0 0 1 100 {title_y_position} Tm
                ({title}) Tj
                ET
            """.encode('utf-8')

        content = Stream(self.pdf, toc_text)

        page_dict = Dictionary({
            '/Type': Name('/Page'),
            '/MediaBox': Array([0, 0, page_width, page_height]),
            '/Resources': self.pdf.make_indirect(resources),
            '/Contents': self.pdf.make_indirect(content)  # Empty content stream
        })

        # Add the page to the PDF
        page = Page(self.pdf.make_indirect(page_dict))
        return page
