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
    _in_file = None
    _connote_header = 'Con Note'
    _connotes = {}

    def __init__(self, file=None):
        """StopParser initialisation.
        """
        if file is not None:
            self._in_file = file

    @property
    def in_file(self):
        return self._in_file

    def set_in_file(self, value):
        self._in_file = value

    @property
    def connote_header(self):
        return self._connote_header

    def set_connote_header(self, value):
        self._connote_header = value

    @property
    def connotes(self):
        return self._connotes

    def set_connotes(self, dict):
        self._connotes[dict[self.connote_header]] = dict

    def connote_lookup(self, connote):
        log.info('Connote lookup: "%s"' % connote)
        return self.connotes.get(connote)

    def read(self):
        """Parses the csv file denoted by :attr:`in_file`.

        """
        if self.in_file is not None:
            try:
                fh = open(self.in_file, 'rb')
                reader = csv.DictReader(fh)
                log.info('Parsing connotes in "%s"' % fh.name)
                for rowdict in reader:
                    self.set_connotes(rowdict)

            except IOError, err:
                log.error('Unable to open file "%s"' % self.in_file)
        else:
            log.warn('No csv file has been provided')

    def purge(self):
        """Release :attr:`connotes` memory resources

        """
        self._connotes.clear()
