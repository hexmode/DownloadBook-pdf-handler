"""Various exceptions."""


class LoginCredsNeededError(Exception):
    """Exception to signal that login credentials are needed."""


class FileNameError(Exception):
    """Exception raised when there is a problem with the file name."""


class MissingSettingError(Exception):
    """Signal that a setting is missing."""


class ParseError(Exception):
    """Signal that something on the page is wrong."""


class NoChapterForSectionError(Exception):
    """Exception thrown if there is no chapter started yet."""


class NoLinkFoundError(Exception):
    """Signal that no link was found where it was expected."""


class NoPageListPageError(Exception):
    """Signal that we couldn't get the page list page."""
