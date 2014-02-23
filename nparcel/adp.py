__all__ = [
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

    .. attribute:: delivery_partners

        list of "delivery_partner" table values

    """
    _headers = {}
    _delivery_partners = []

    def __init__(self, **kwargs):
        """Adp initialisation.

        """
        super(nparcel.Adp, self).__init__(db=kwargs.get('db'))

        self.set_headers(kwargs.get('headers'))
        self.set_delivery_partners(kwargs.get('delivery_partners'))

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

    @property
    def delivery_partners(self):
        return self._delivery_partners

    def set_delivery_partners(self, values=None):
        del self._delivery_partners[:]
        self._delivery_partners = []

        if values is not None:
            self._delivery_partners.extend(values)
            log.debug('delivery partners list: "%s"' %
                      self.delivery_partners)

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

        log.info('Processing Agent code: "%s" ...' % code)
        filtered_values = self.extract_values(values)

        sanitised_values = self.sanitise(filtered_values)
        if not self.validate(sanitised_values):
            status = False
            self.set_alerts('Agent code "%s" validation error' % code)

        if status:
            # Check if the code already exists.
            sql = self.db.agent.check_agent_id(code)
            self.db(sql)
            rows = list(self.db.rows())
            if len(rows) > 0:
                self.set_alerts('Agent code "%s" already exists' % code)
            else:
                # Agent table.
                agent_values = {}
                for k, v in sanitised_values.iteritems():
                    if 'agent.' in k:
                        agent_values[k.replace('agent.', '')] = v
                self.db.insert(self.db.agent.insert_sql(agent_values))

        log.info('Agent code "%s" load status: %s' % (code, status))

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

        * ``delivery_partner.id`` must convert the delivery partner name
          to the ``delivery_partner.id`` column value

        **Args:**
            *values*: dictionary of table column headers and values.

        **Returns:**
            dictionary of sanitised values

        """
        sanitised_values = copy.deepcopy(values)

        # agent.status
        status = values.get('agent.status')
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

            sanitised_values['agent.status'] = status

        # Delivery partner.
        column = 'delivery_partner.id'
        dp = values.get(column)
        if dp is not None:
            log.debug('Sanitising "%s" value: "%s" ...' % (column, dp))
            index = None
            try:
                index = self.delivery_partners.index(dp) + 1
                log.debug('Found "%s" value index at %d' % (dp, index))
            except ValueError, err:
                log.error('"%s" lookup failed' % dp)

            if index is not None:
                sanitised_values[column] = index
            else:
                sanitised_values.pop(column)

        return sanitised_values

    def validate(self, values):
        """Hardwired validator rules that need to be applied to bulk
        insert data before being inserted into the database.

        .. note::

            "hardwired" because of bad design :-(

        Current sanitisation rules include:

        * The ``agent.status`` value needs to an integer

        * ``delivery_partner.id`` must contain a value

        **Args:**
            *values*: dictionary of table column headers and values.

        **Returns:**
            boolean ``True`` if the validation is OK

            boolean ``False`` otherwise

        """
        is_valid = True

        # Status.
        status = values.get('agent.status')
        if (status is not None and type(status) is not int):
            is_valid = False
            self.set_alerts('"status" validation failed type check: %s' %
                             type(status))

        # Postcode.
        postcode = values.get('agent.postcode')
        if (postcode is not None):
            translated_state = translate_postcode(postcode)
            state = values.get('agent.state')
            if state is None:
                log.info('State missing - using "%s"' % translated_state)
            else:
                if state != translated_state:
                    self.set_alerts('State/postcode "%s/%s" mismatch' %
                                    (state, postcode))
                    is_valid = False

        # Delivery partner.
        dp = values.get('delivery_partner.id')
        if dp is None:
            self.set_alerts('Deliver partner invalid value')
            is_valid = False

        if not is_valid:
            log.info('Validation failed')

        return is_valid

    def reset(self, commit=False):
        """Initialise object state in readiness for another iteration.
        """
        self.set_alerts()

        if commit:
            log.info('Committing transaction state to the DB ...')
            self.db.commit()
            log.info('Commit OK')
        else:
            log.info('Rolling back transaction state to the DB ...')
            self.db.rollback()
            log.info('Rollback OK')
