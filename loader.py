__all__ = [
    "Loader",
]
import nparcel

FIELDS = {'Bar code': {'offset': 438,
                       'length': 15}}

class Loader(object):
    """Nparcel Loader object.
    """

    def __init__(self):
        """
        """
        self.parser = nparcel.Parser(fields=FIELDS)
