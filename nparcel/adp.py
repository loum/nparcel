_d_all__ = [
    "Adp",
]
import copy

import nparcel
from nparcel.utils.log import log
from nparcel.postcode import translate_postcode


class Adp(nparcel.Service):
    """Adp (Alternate Delivery Point) class.

    .. attribute:: headers

        dictionary of ``agent`` column keys and corresponding ADP bulk
        insert file header values.  For example::

            {'code': 'TP Code',
             'dp_code':  'DP Code',
             'name': 'ADP Name'}

    """
    _headers = {}

    def __init__(self, **kwargs):
        """Adp initialisation.

        """
        super(nparcel.Adp, self).__init__(db=kwargs.get('db'))

        self.set_headers(kwargs.get('headers'))

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

    def process(self, code, values, dry=False):
        """Parses an ADP bulk insert file and attempts to load the items
        into the ``agent`` table.

        **Kwargs:**
            *code*: value that typically relates to the ``agent.code``
            column

            *values*: dictionary of raw values to load into the
            Toll Parcel Portal database

            *dry*: only report, do not execute

        **Returns:**
            boolean ``True`` if processing was successful

            boolean ``False`` if processing failed

            ``None`` if an *other* scenario (typically a record ignore)

        """
        status = True

        log.debug('Processing Agent code: "%s"' % code)
        filtered_values = self.extract_values(values)

        sanitised_values = self.sanitise(filtered_values)
        if not self.validate(sanitised_values):
            status = False

        if status:
            # Check if the code already exists.
            sql = self.db.agent.check_agent_id(code)
            self.db(sql)
            rows = list(self.db.rows())
            if len(rows) > 0:
                log.error('Code "%s" already exists' % code)
            else:
                self.db.insert(self.db.agent.insert_sql(sanitised_values))

        return status

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

    def sanitise(self, values):
        """Hardwired sanitiser rules that need to be applied to bulk
        insert data before being inserted into the database.

        .. note::

            "hardwired" because of bad design :-(

        Current sanitisation rules include:

        * The ``agent.status`` value need to be converted from:

          * ``YES`` or ``1`` to integer 1

          * ``NO`` or ``2`` to integer 2

        **Args:**
            *values*: dictionary of table column headers and values.

        **Returns:**
            dictionary of sanitised values

        """
        log.debug('sanitise value: %s' % values)
        sanitised_values = copy.deepcopy(values)

        # agent.status
        status = values.get('status')
        if status is not None:
            log.debug('Sanitising "status" value: "%s" ...' % status)
            try:
                status = int(status)
            except ValueError, err:
                if status.lower() == 'no':
                    status = 2
                elif status.lower() == 'yes':
                    status = 1
                log.debug('"status" is text.  New value: "%s"' % status)

            sanitised_values['status'] = status

        return sanitised_values

    def validate(self, values):
        """Hardwired validator rules that need to be applied to bulk
        insert data before being inserted into the database.

        .. note::

            "hardwired" because of bad design :-(

        Current sanitisation rules include:

        * The ``agent.status`` value needs to an integer.

        **Args:**
            *values*: dictionary of table column headers and values.

        **Returns:**
            boolean ``True`` if the validation is OK

            boolean ``False`` otherwise

        """
        is_valid = True

        # Status.
        status = values.get('status')
        if (status is not None and type(status) is not int):
            is_valid = False
            log.error('"status" validation failed type check: %s' %
                      type(status))

        postcode = values.get('postcode')
        if (postcode is not None):
            translated_state = translate_postcode(postcode)
            state = values.get('state')
            if state is None:
                log.info('State missing - using "%s"' % translated_state)
            else:
                if state != translated_state:
                    log.error('State/postcode "%s/%s" mismatch' %
                              (state, postcode))
                    is_valid = False

        if not is_valid:
            log.info('Validation failed')

        return is_valid
