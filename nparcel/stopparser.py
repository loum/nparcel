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
    _connote_header = 'Consignment Number'
    _arrival_header = 'Delivery Date'
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
    def arrival_header(self):
        return self._arrival_header

    def set_arrival_header(self, value):
        self._arrival_header = value

    @property
    def connotes(self):
        return self._connotes

    def set_connotes(self, dict):
        self._connotes[dict[self.connote_header]] = dict

    def connote_lookup(self, connote):
        return self.connotes.get(connote)

    def connote_delivered(self, connote):
        """Check if *connote* has been "delivered".

        .. note::

            Delivered suggests that the connote has an 'Actual Delivered'
            timestamp in the TCD Delivery Report.

        **Args:**
            *connote*: connote relating to the ``jobitem.connote_nbr``
            column.

        **Returns:**
            boolean ``True`` if *connote* has been delivered
            boolean ``False`` otherwise

        """
        log.debug('TCD checking connote "%s" delivery status' % connote)

        delivered = False
        item = self.connote_lookup(connote)
        if item is not None:
            if item[self.arrival_header]:
                delivered = True

        log.debug('Connote "%s" delivery status: %s' % (connote, delivered))

        return delivered

    def read(self):
        """Parses the contents of file denoted by :attr:`in_file`.

        """
        if self.in_file is not None:
            try:
                fh = open(self.in_file, 'rb')
                fieldnames = ['Consignment Number',
                              'Despatch Date',
                              'Item Number',
                              'Delivery Date']
                reader = csv.DictReader(fh,
                                        delimiter=' ',
                                        skipinitialspace=True,
                                        fieldnames=fieldnames)
                log.debug('Parsing connotes in "%s"' % fh.name)
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
