"""Various exceptions."""


class LoginCredsNeededError(Exception):
    """Exception to signal that login credentials are needed."""


class FileNameError(Exception):
    """Exception raised when there is a problem with the file name."""


class MissingSettingError(Exception):
    """Signal that a setting is missing."""
