"""Class to hold the links."""


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
