__all__ = [
    "StopParser",
]
import csv

from nparcel.utils.log import log


class StopParser(object):
    """GraysOnline Shipment Stop Report parser.

    .. attribute:: fields

        A dictionary based data structure that identifies the elements
        of interest.

    .. attribute:: in_file

        csv file to parse

    """
    _fields = {}
    _in_file = None

    def __init__(self, fields=None):
        """StopParser initialisation.
        """
        if fields is not None:
            self._fields = fields

    @property
    def fields(self):
        return self._fields

    def set_fields(self, value):
        if isinstance(value, dict):
            for k, v in value.iteritems():
                self._fields[k] = v
        else:
            raise TypeError('Token assignment expected dictionary')

    @property
    def in_file(self):
        return self._in_file

    def set_in_file(self, value):
        self._in_file = value

    def read(self, column=None):
        """Parses the csv file denoted by :attr:`in_file`.

        **Args:**
            *column*: the CSV header to extract.  For example, "Con Note".

        """
        if self.in_file is not None:
            try:
                fh = open(self.in_file, 'rb')
                reader = csv.DictReader(fh)
                for rowdict in reader:
                    yield rowdict.pop(column)
            except IOError, err:
                log.error('Unable to open file "%s"' % self.in_file)
        else:
            log.warn('No csv file has been provided')
