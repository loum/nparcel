__all__ = [
    "Writer",
]
import csv

from nparcel.utils.log import log


class Writer(object):
    """Toll Parcel Portal Writer class.

    .. attribute:: outfile
        name of the output file to write to

    .. attribute:: headers
        name and order of the column headers

    .. attribute:: write_headers
        write the column names in the first row (default ``True``)

    """
    _outfile = None
    _headers = []
    _write_headers = True

    def __init__(self, outfile=None):
        """Writer initialiser.

        """
        if outfile is not None:
            self._outfile = outfile

    def __call__(self, data):
        """Class callable that writes list of tuple values in *data*.

        **Args:**
            *data*: list of tuples to write out

        """
        log.debug('Preparing "%s" for output' % self.outfile)
        fh = open(self.outfile, 'wb')

        writer = csv.DictWriter(fh, delimiter=',', fieldnames=self.headers)
        if self.write_headers:
            writer.writerow(dict((fn, fn) for fn in self.headers))

        for row in data:
            writer.writerow(dict(zip(self.headers, row)))

        fh.close()

    @property
    def outfile(self):
        return self._outfile

    def set_outfile(self, value=None):
        self._outfile = value

    @property
    def headers(self):
        return self._headers

    def set_headers(self, values=None):
        del self._headers[:]
        self._headers = []

        if values is not None and isinstance(values, list):
            log.debug('Setting headers to "%s"' % str(values))
            self._headers.extend(values)

    @property
    def write_headers(self):
        return self._headers

    def set_write_headers(self, value=False):
        self._write_headers = value
