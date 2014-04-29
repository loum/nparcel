__all__ = [
    "StopParser",
]
import csv

from top.utils.log import log


class StopParser(object):
    """GraysOnline Shipment Stop Report parser.

    .. attribute:: fields

        A dictionary based data structure that identifies the elements
        of interest.

    .. attribute:: in_files

        list of file to parse

    """
    _in_files = []
    _connote_header = 'Consignment Number'
    _item_header = 'Item Number'
    _arrival_header = 'Delivery Date'
    _connotes = {}

    def __init__(self, files=None):
        """StopParser initialisation.
        """
        if files is not None:
            self.set_in_files(files)

    @property
    def in_files(self):
        return self._in_files

    def set_in_files(self, values):
        del self._in_files[:]
        self._in_files = []

        if values is not None:
            self._in_files.extend(values)
            log.debug('Set input files to: %s' % self._in_files)

    @property
    def connote_header(self):
        return self._connote_header

    def set_connote_header(self, value):
        self._connote_header = value

    @property
    def item_header(self):
        return self._item_header

    def set_item_header(self, value):
        self._item_header = value

    @property
    def arrival_header(self):
        return self._arrival_header

    def set_arrival_header(self, value):
        self._arrival_header = value

    @property
    def connotes(self):
        return self._connotes

    @property
    def size(self):
        return len(self._connotes)

    def set_connotes(self, dict):
        connote = dict[self.connote_header]
        if self._connotes.get(connote) is None:
            self._connotes[connote] = []

        item_nbr = dict.get(self.item_header)
        item_found = False
        for item in self._connotes.get(connote):
            this_item = item.get(self.item_header)
            if this_item is not None and this_item == item_nbr:
                item_found = True
                break

        if not item_found:
            self._connotes[connote].append(dict)

    def connote_lookup(self, connote):
        return self.connotes.get(connote)

    def connote_delivered(self, connote, item_nbr=None):
        """Check if *connote* has been "delivered".

        .. note::

            Delivered suggests that the connote has an 'Actual Delivered'
            timestamp in the TCD Delivery Report.

        **Args:**
            *connote*: connote relating to the ``jobitem.connote_nbr``
            column

        **Kwargs:**
            *item_nbr*: item number relating to the ``jobitem.item_nbr``
            column

        **Returns:**
            boolean ``True`` if *connote* has been delivered

            boolean ``False`` otherwise

        """
        log.debug('TCD checking connote "%s" delivery status' % connote)

        delivered = False
        lookup_list = self.connote_lookup(connote)
        if lookup_list is not None:
            for lookup in lookup_list:
                # Just cycle through the dictionary list with an
                # anonymous item number.
                if item_nbr is None:
                    if lookup.get(self.arrival_header) is not None:
                        delivered = True
                else:
                    if ((lookup.get(self.item_header) is not None) and
                        (lookup.get(self.item_header) == item_nbr and
                        (lookup.get(self.arrival_header) is not None))):
                        delivered = True

                if delivered:
                    break

        log.debug('Connote "%s" delivery status: %s' % (connote, delivered))

        return delivered

    def read(self):
        """Parses the contents of file denoted by :attr:`in_files`.

        """
        for f in self.in_files:
            try:
                log.debug('Parsing connotes in "%s"' % f)
                fh = open(f, 'rb')
                fieldnames = ['Consignment Number',
                              'Despatch Date',
                              'Item Number',
                              'Delivery Date']
                reader = csv.DictReader(fh,
                                        delimiter=' ',
                                        skipinitialspace=True,
                                        fieldnames=fieldnames)
                for rowdict in reader:
                    self.set_connotes(rowdict)

            except IOError, err:
                log.error('Unable to open file "%s"' % f)

    def purge(self):
        """Release :attr:`connotes` memory resources

        """
        self._connotes.clear()
