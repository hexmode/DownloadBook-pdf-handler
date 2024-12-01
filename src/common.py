"""Some common things to be shared."""

from pikepdf import Dictionary, Name


class Common:
    """Represent a common utility class."""

    LINE_HEIGHT = 20
    # Font size for header and footer
    HF_FONT_SIZE = 10
    HF_FONT_SIGN = "/F2"
    MARGIN = 72

    # 8.5x11 inches
    PAGE_HEIGHT = 792
    PAGE_WIDTH = 612

    # Identity transform
    ID_TRANSFORM = "1 0 0 1"

    @staticmethod
    def header(text: str, font_size: int = HF_FONT_SIZE, font_sign: str = HF_FONT_SIGN) -> bytes:
        """
        Return the header as bytes.

        Parameters
        ----------
        text : str
            The text to put in the header.
        font_size : int
            The size of the font.
        font_sign : str
            The PDF reference for this font.

        Returns
        -------
        str
            The formatted header.
        """
        return f"""q
               BT
               {font_sign} {font_size} Tf
               {Common.ID_TRANSFORM} {Common.MARGIN} {Common.PAGE_HEIGHT - Common.MARGIN + 2 * font_size} Tm
               ({text}) Tj
               ET
               Q""".encode()

    @staticmethod
    def footer(text: str, font_size: int = HF_FONT_SIZE, font_sign: str = HF_FONT_SIGN) -> bytes:
        """
        Return the footer as bytes.

        Parameters
        ----------
        text : str
            The text to put in the header.
        font_size : int
            The size of the font.
        font_sign : str
            The PDF reference for this font.

        Returns
        -------
        str
            The formatted footer.
        """
        return f"""q
               BT
               {font_sign} {font_size} Tf
               {Common.ID_TRANSFORM} {Common.MARGIN} {Common.MARGIN - font_size} Tm
               ({text}) Tj
               ET
               Q""".encode()

    @staticmethod
    def font_dictionary(font_name: str = "Helvetica") -> Dictionary:
        """
        Return a dictionary representing a standard PDF font.

        Parameters
        ----------
        font_name : str
            The name of the font we want.

        Returns
        -------
        Dictionary
            A dictionary containing font details for a standard PDF font.
        """
        return Dictionary(
            {
                "/Type": Name.Font,
                "/Subtype": Name("/Type1"),
                "/BaseFont": Name(f"/{font_name}"),  # Standard PDF font
            }
        )

    @staticmethod
    def calculate_text_width(text: str, font_size: int) -> float:
        """
        Calculate the width of rendered text in PDF space.

        Parameters
        ----------
        text : str
            The string to measure.
        font_size : int
            The font size of the text.

        Returns
        -------
        float
            The width of the text in points, suitable for PDF dimensions.
        """
        # Assume a typical font width of 0.5 times the font size per character (can be adjusted for your font)
        avg_char_width = 0.5 * font_size
        return len(text) * avg_char_width
