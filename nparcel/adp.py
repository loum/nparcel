__all__ = [
    "Adp",
]
import nparcel
from nparcel.utils.log import log


class Adp(nparcel.Service):
    """Adp (Alternate Delivery Point) class.

    .. attribute:: parser

        :mod:`nparcel.AdpParser` parser object

    .. attribute:: headers

        dictionary of ``agent`` column keys and corresponding ADP bulk
        insert file header values.  For example::

            {'code': 'TP Code',
             'dp_code':  'DP Code',
             'name': 'ADP Name'}

    """
    _parser = nparcel.AdpParser()
    _headers = {}

    def __init__(self, db_kwargs=None):
        """Adp initialisation.

        """
        super(nparcel.Adp, self).__init__(db=db_kwargs)

    @property
    def parser(self):
        return self._parser

    @property
    def headers(self):
        return self._headers

    def set_headers(self, values=None):
        self._headers.clear()

        if values is not None:
            self._headers = values
            log.debug('Headers set to: "%s"' % self.headers)
        else:
            log.debug('Cleared headers')

    def process(self, in_files=None, dry=False):
        """Parses an ADP bulk insert file and attempts to load the items
        into the ``agent`` table.

        **Kwargs:**
            *in_files*: list of paths to the input file

            *dry*: only report, do not execute

        """
        if in_files is not None:
            self.parser.set_in_files(in_files)
            self.parser.read()

        for code, v in self.parser.adps.iteritems():
            log.debug('Processing Agent code: "%s"' % code)
            values = self.extract_values(v)

            # Check if the code already exists.
            sql = self.db.agent.check_agent_id(code)
            self.db(sql)
            rows = list(self.db.rows())
            if len(rows) > 0:
                log.error('Code "%s" already exists' % code)
            else:
                self.db.insert(self.db.agent.insert_sql(values))

    def extract_values(self, dict):
        """Takes the raw values presented by *dict* and extracts the
        required values as per the :attr:`headers` values.

        **Args:**
            *dict*: dictionary of values that represent a raw line item
            taken directly from the ADP bulk insert file

        **Returns**:
            the values that are extracted from the raw *dict* structure

        """
        filtered_dict = {}

        for k, h in self.headers.iteritems():
            filtered_dict[k] = dict.get(h)

        return filtered_dict
