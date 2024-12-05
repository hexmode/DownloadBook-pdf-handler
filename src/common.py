"""Some common things to be shared."""

from pikepdf import Dictionary, Name
from PIL import ImageFont


class Common:
    """Represent a common utility class."""

    LINE_HEIGHT = 20
    # Font size for header and footer
    HF_FONT_SIZE = 10
    HF_FONT_SIGN = "/F2"
    MARGIN = 72

    FONT_FAMILY = "Arial"
    FONT_FAMILY_PATH = "/usr/share/fonts/truetype/croscore/Arimo-Regular.ttf"

    # 8.5x11 inches
    PAGE_HEIGHT = 792
    PAGE_WIDTH = 612

    # Identity transform
    ID_TRANSFORM = "1 0 0 1"

    @staticmethod
    def text_width(text: str, font_size: int, font_path: str = FONT_FAMILY_PATH) -> float:
        """
        Calculate the width of a given text string when rendered with a specific font and size.

        Parameters
        ----------
        text : str
            The text string whose width is to be measured.
        font_size : int
            The size of the font to be used for rendering the text.
        font_path : str, optional
            The path to the font file to be used for rendering the text.
            Defaults to FONT_FAMILY_PATH.

        Returns
        -------
        float
            The width of the rendered text in pixels.
        """
        font = ImageFont.truetype(font_path, font_size)
        return font.getlength(text)

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
        bytes
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
        bytes
            The formatted footer.
        """
        text_width = Common.text_width(text, font_size)
        x_position = Common.PAGE_WIDTH - text_width - Common.MARGIN

        return f"""q
               BT
               {font_sign} {font_size} Tf
               {Common.ID_TRANSFORM} {x_position} {Common.MARGIN - font_size} Tm
               ({text}) Tj
               ET
               Q""".encode()

    @staticmethod
    def font_dictionary(font_name: str = FONT_FAMILY) -> Dictionary:
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
    def int_to_roman(num: int) -> str:
        """
        Given num, produce a lower-case roman numeral equivalent.

        Parameters
        ----------
        num : int
            The number we need a roman numeral for.

        Returns
        -------
        str
            The roman numeral equivalent.
        """
        roman_map = [
            (1000, "m"),
            (900, "cm"),
            (500, "d"),
            (400, "cd"),
            (100, "c"),
            (90, "xc"),
            (50, "l"),
            (40, "xl"),
            (10, "x"),
            (9, "ix"),
            (5, "v"),
            (4, "iv"),
            (1, "i"),
        ]
        result = []
        for value, numeral in roman_map:
            while num >= value:
                result.append(numeral)
                num -= value
        return "".join(result)
