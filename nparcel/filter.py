__all__ = [
    "Filter",
]
import nparcel
from nparcel.utils.log import log

# ParcelPoint records are only interested in the "Agent Id" field.
FIELDS = {'Agent Id': {'offset': 453,
                       'length': 4}}


class Filter(object):
    """Nparcel Filter object.

    """
    _parser = nparcel.Parser(fields=FIELDS)

    @property
    def parser(self):
        return self._parser
