__all__ = [
    "Adp",
]
import datetime
import copy

import top
from top.utils.log import log
from top.utils.setter import (set_list,
                              set_dict)
from top.postcode import translate_postcode


class Adp(top.Service):
    """Adp (Alternate Delivery Point) class.

    .. attribute:: headers

        dictionary of ``agent`` column keys and corresponding ADP bulk
        insert file header values.  For example::

            {'code': 'TP Code',
             'dp_code':  'DP Code',
             'name': 'ADP Name'}

    .. attribute:: delivery_partners

        list of "delivery_partner" table values

    .. attribute:: default_passwords

        dictionary of delivery partner default passwords

    """
    _headers = {}
    _delivery_partners = []
    _default_passwords = {}

    @property
    def parser(self):
        return self._parser

    @property
    def headers(self):
        return self._headers

    @set_dict
    def set_headers(self, values=None):
        pass

    @property
    def delivery_partners(self):
        return self._delivery_partners

    @set_list
    def set_delivery_partners(self, values=None):
        pass

    @property
    def default_passwords(self):
        return self._default_passwords

    @set_dict
    def set_default_passwords(self, values=None):
        pass

    def __init__(self, **kwargs):
        """Adp initialisation.

        """
        top.Service.__init__(self, db=kwargs.get('db'))

        self.set_headers(kwargs.get('headers'))
        self.set_delivery_partners(kwargs.get('delivery_partners'))
        self.set_default_passwords(kwargs.get('default_passwords'))

    def process(self, code, values, dry=False):
        """Parses an ADP bulk insert file and attempts to load the items
        into the ``agent`` table.

        **Kwargs:**
            *code*: value that typically relates to the ``agent.code``
            column

            *values*: dictionary of raw values to load into the
            Toll Outlet Portal database

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
                status = False
                self.set_alerts('Agent code "%s" already exists' % code)
            else:
                # Agent table.
                ts = datetime.datetime.now().isoformat(' ').split('.', 1)[0]
                sanitised_values['agent.created_ts'] = ts
                username = sanitised_values.get('login_account.username')
                sanitised_values['agent.username'] = username
                agent_values = {}
                for k, v in sanitised_values.iteritems():
                    if 'agent.' in k:
                        agent_values[k.replace('agent.', '')] = v
                self.db.insert(self.db.agent.insert_sql(agent_values))

                # Login account table.
                login_values = {}
                for k, v in sanitised_values.iteritems():
                    if 'login_account.' in k:
                        login_values[k.replace('login_account.', '')] = v
                sql = self.db.login_account.insert_sql(login_values)
                self.db.insert(sql)

                # Login access access.
                # This is hardwired fugliness.
                dp = sanitised_values.get('delivery_partner.id')
                access_values = {'username': username,
                                 'dp_id': dp,
                                 'sla_id': 4}
                sql = self.db.login_access.insert_sql(access_values)
                self.db.insert(sql)

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

        * ``login_account.username`` must have an associated password

        * ``login_account.status`` value to be converted from:

          * ``YES`` or ``Y`` to integer 1

          * ``NO`` or ``N`` to integer 0

        * ``agent.parcel_size_code`` value defaults to "S" if no valid
          option is provided

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
            log.debug('Sanitising delivery_partner "%s" value: "%s" ...' %
                      (column, dp))
            index = None
            try:
                index = self.delivery_partners.index(dp) + 1
                log.debug('Found "%s" value index at %d' % (dp, index))
            except ValueError, err:
                log.error('"%s" lookup failed' % dp)

            if index is not None:
                sanitised_values[column] = index
                sanitised_values['agent.dp_id'] = index
            else:
                sanitised_values.pop(column)

        # Password.
        log.debug('Sanitising password ...')
        if dp is not None:
            pw = self.default_passwords.get(dp.lower())
            if pw is not None:
                sanitised_values['login_account.password'] = pw

        if sanitised_values.get('login_account.password') is None:
            self.set_alerts('Password lookup failed')

        # login_account.status
        log.debug('Sanitising login_account.status ...')
        la_status = values.get('login_account.status')
        if la_status is not None:
            try:
                la_status = int(la_status)
            except ValueError, err:
                if (la_status.lower() == 'no' or
                    la_status.lower() == 'n'):
                    la_status = 0
                elif (la_status.lower() == 'yes' or
                      la_status.lower() == 'y'):
                    la_status = 1
                log.debug('"login_account.status": %s new value: "%s"' %
                          (values.get('login_account.status'), la_status))
        else:
            # Enable by default.
            la_status = 1

        sanitised_values['login_account.status'] = la_status

        # agent.parcel_size_code
        log.debug('Sanitising agent.parcel_size_code ...')
        ag_parcel_size_code = values.get('agent.parcel_size_code')
        if (ag_parcel_size_code is None or
            not len(ag_parcel_size_code)):
            log.info('%s missing. Setting to "S"' %
                     'agent.parcel_size_code')
            ag_parcel_size_code = 'S'

        if (ag_parcel_size_code != 'S' and
            ag_parcel_size_code != 'L'):
            log.info('%s value "%s" unknown. Setting to "S"' %
                     ('agent.parcel_size_code', ag_parcel_size_code))
            ag_parcel_size_code = 'S'

        sanitised_values['agent.parcel_size_code'] = ag_parcel_size_code

        return sanitised_values

    def validate(self, values):
        """Hardwired validator rules that need to be applied to bulk
        insert data before being inserted into the database.

        .. note::

            "hardwired" because of bad design :-(

        Current validation rules include:

        * The ``agent.status`` value needs to an integer

        * ``delivery_partner.id`` must contain a value

        * ``login_account.username`` must have an associated password

        **Args:**
            *values*: dictionary of table column headers and values

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
        if (postcode is not None and postcode):
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

        # Username / password.
        username = values.get('login_account.username')
        pw = values.get('login_account.password')
        if username is None:
            self.set_alerts('Username undefined')
        elif pw is None:
            self.set_alerts('Username "%s" - undefined password' % username)

        if username is None or pw is None:
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
