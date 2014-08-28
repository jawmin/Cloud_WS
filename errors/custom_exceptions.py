__author__ = 'benoit'


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class BundleError(Error):
    """
    Raised if a bundle is incorrectly configured
    """
    def __init__(self, message, error=None):
        self.message = message
        self.error = error


class DatabaseError(Error):
    """
    Raised if a database error is detected
    """
    def __init__(self, message, error=None):
        self.message = message
        self.error = error


class JujuError(Error):
    """
    Raised if an error is detected when communicating with Juju
    """
    def __init__(self, message, error):
        self.message = message
        self.error = error