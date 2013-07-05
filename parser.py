__all__ = [
    "Parser",
]
from nparcel.utils.log import class_logging

@class_logging
class Parser(object):
    """1250 file parser.
    """

    def __init__(self):
        """Parser initialisation.
        """
        self._tokens = None

    @property
    def tokens(self):
        return self._tokens

    @tokens.setter
    def tokens(self, value):
        self._tokens = value
