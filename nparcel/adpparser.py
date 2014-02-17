__all__ = [
    "AdpParser",
]
import csv

from nparcel.utils.log import log


class AdpParser(object):
    """Alternate Delivery Point (ADP) parser.

    """
    _in_files = []
    _dp_code_header = 'DP Code'
    _adps = {}

    def __init__(self, files=None):
        """AdpParser initialisation.
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
    def adps(self):
        return self._adps

    @property
    def dp_code_header(self):
        return self._dp_code_header

    def set_dp_code_header(self, value):
        self._dp_code_header = value

    def read(self, files=None):
        """Parses the contents of file denoted by :attr:`in_files`.

        **Kwargs**:
            *files*: override the list of files to parse

        """
        files_to_parse = []

        if files is not None:
            files_to_parse.extend(files)
        else:
            files_to_parse.extend(self.in_files)

        for f in self.in_files:
            try:
                log.debug('Parsing connotes in "%s"' % f)
                fh = open(f, 'rb')
                reader = csv.DictReader(fh)
                for rowdict in reader:
                    self.set_adps(rowdict)

            except IOError, err:
                log.error('Unable to open file "%s"' % f)

    def set_adps(self, dict):
        dp_code = dict.get(self.dp_code_header)
        log.debug('dp_code_header value: %s' % dp_code)

        self._adps[dp_code] = dict

    def adp_lookup(self, dp_code):
        return self.adps.get(dp_code)
