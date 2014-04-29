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
        log.debug('Setting outfile to "%s"' % value)
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

    def filter(self, headers, headers_displayed, row):
        """Takes a list of column *headers* and filters the *row*
        based on the list of *headers_displayed*.

        **Args:**
            *headers*: all column headers

            *headers_displayed*: headers to display

            *row*: tuple-based column values

        **Returns:**
            tuple of filtered *row* values

        """
        log.debug('Filtering out data to display for row: "%s"' % str(row))

        new_row_list = []
        for i in headers_displayed:
            log.debug('Extracting header "%s" value' % i)
            try:
                index = headers.index(i)
                value = row[index]
                log.debug('Header "%s" value is "%s"' % (i, value))
                new_row_list.append(value)
            except ValueError:
                log.warn('Header to display "%s" not in column list' % i)

        return tuple(new_row_list)

    def header_aliases(self, headers_displayed, header_aliases):
        """Substitute the raw header_values in *headers_displayed* with
        the aliases defined in *header_alises*.

        **Args:**
            *headers_displayed*: headers to display

            *header_aliases*: dictionary structure that maps the raw
            header value to the alias.  Typical form is::

                {'AGENT_NAME': 'Agent Name',
                 ...}

        """
        log.debug('Substituting header aliases as per: "%s"' %
                  str(header_aliases))

        new_header_list = []
        for i in headers_displayed:
            log.debug('Substituting alias for header "%s"' % i)
            alias = header_aliases.get(i)
            if alias is not None:
                log.debug('Header "%s" alias is "%s"' % (i, alias))
                new_header_list.append(alias)
            else:
                log.debug('Header "%s" has no alias' % i)
                new_header_list.append(i)

        return new_header_list
