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

    def process(self, code, values, mode='insert'):
        """Parses an ADP bulk insert file and attempts to load the items
        into the ``agent`` table.

        **Args:**
            *code*: value that typically relates to the ``agent.code``
            column

            *values*: dictionary of raw values to load into the
            Toll Outlet Portal database

        **Kwargs:**
            *mode*: the mode of operation.  Defaults to "insert"

        **Returns:**
            boolean ``True`` if processing was successful

            boolean ``False`` if processing failed

        """
        log.info('Processing (%s) Agent code: "%s" ...' % (mode, code))
        filtered_values = self.extract_values(values)

        status = False
        if mode == 'insert':
            status = self.insert(code, filtered_values)
        elif mode == 'update':
            status = self.update(code, filtered_values)
        else:
            log.error('Unknown mode: "%s"' % self.mode)

        log.info('Agent code "%s" load status: %s' % (code, status))

        return status

    def insert(self, code, values):
        """Insert the *values* into the database.

        Provides an additional :meth:`sanitise` step to cleanse data.

        **Args:**
            *code*: value that typically relates to the ``agent.code``
            column

            *values*: dictionary of raw values to load into the
            Toll Outlet Portal database

        **Returns:**
            boolean ``True`` if processing was successful

            boolean ``False`` if processing failed

        """
        status = True

        sanitised_values = self.sanitise(values)
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

        return status

    def update(self, code, values):
        """Update *values* into the database.

        Will attempt to filter the *values* as per
        :meth:`filter_update_fields` and group per table before
        applying the udpates.

        **Args:**
            *code*: value that typically relates to the ``agent.code``
            column

            *values*: dictionary of raw values to load into the
            Toll Outlet Portal database

        **Returns:**
            boolean ``True`` if processing was successful

            boolean ``False`` if processing failed

        """
        status = True

        # agent table updates.
        agent_values = self.filter_update_fields(values, key='agent')
        if agent_values.get('agent.status') is not None:
            value = agent_values.get('agent.status')
            agent_values['agent.status'] = self.sanitise_agent_status(value)

        if agent_values.get('agent.parcel_size_code') is not None:
            value = agent_values.get('agent.parcel_size_code')
            sanitised_val = self.sanitise_agent_parcel_size_code(value)
            agent_values['agent.parcel_size_code'] = sanitised_val

        log.debug('agent update values: %s' % agent_values)

        tmp_agent_values = {}
        for k, v in agent_values.iteritems():
            new_key = k.replace('agent.', '')
            tmp_agent_values[new_key] = v

        agent_values.clear()
        agent_values = dict(tmp_agent_values)

        # Get the current agent.code id
        sql = self.db.agent.agent_code_sql(code)
        self.db(sql)
        rows = list(self.db.rows())
        update_ids = tuple([x[0] for x in rows])
        log.debug('agent table IDs to update: "%s"' % str(update_ids))

        if len(update_ids):
            dml = self.db.agent.update_sql(agent_values, keys=update_ids)
            try:
                self.db(dml)
            except Exception, e:
                log.error('agent table update for code "%s" failed: %s' %
                        (code, e))
        else:
            log.error('No agent.id values provided. Update ignored')

            status = False

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
        """Hardwired sanitiser rules that need to be applied to bulk ADP
        data before being inserted into the database.

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

        column = values.get('agent.status')
        if column is not None:
            sanitised_value = self.sanitise_agent_status(column)
            sanitised_values['agent.status'] = sanitised_value

        column = values.get('agent.parcel_size_code')
        ag_parcel_size_code = self.sanitise_agent_parcel_size_code(column)
        sanitised_values['agent.parcel_size_code'] = ag_parcel_size_code

        delivery_partner = values.get('delivery_partner.id')
        if 'delivery_partner.id' in values:
            dp_id = self.sanitise_delivery_partner_id(delivery_partner)
            if dp_id is not None:
                sanitised_values['delivery_partner.id'] = dp_id
                sanitised_values['agent.dp_id'] = dp_id
            else:
                sanitised_values.pop('delivery_partner.id')

        # Password.
        log.debug('Sanitising login_account.password ...')
        if delivery_partner is not None:
            pw = self.default_passwords.get(delivery_partner.lower())
            if pw is not None:
                sanitised_values['login_account.password'] = pw
            else:
                self.set_alerts('login_account.password lookup failed')

        la_status = values.get('login_account.status')
        conv_la_status = self.sanitise_login_account_status(la_status)
        sanitised_values['login_account.status'] = conv_la_status

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
        if values.get('delivery_partner.id') is None:
            self.set_alerts('deliver_partner.id not defined')
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

    def sanitise_agent_status(self, value):
        """Prepares the agent.status value for further table column
        adjustment.

        ``agent.status`` stores its value as an integer value as per:

        * ``0`` for *no/inactive*
        * ``1`` for *yes/active*
        * ``2`` for *test*.

        This was a database design constraint.  We're
        simply adhering to the design, regardless of how bad it is.

        To be more intuitive to the user preparing the ADP input file, we
        need to translate the user values to their corresponding table
        column values.  Currently, this method supports the following
        case-insentive values:

        * *no/inactive* is transposed to the integer value 0

        * *yes/active* is transposed to the integer value 1

        * *test* is transposed to the integer value 2

        .. note::

            if you think you know what you are doing, you can pass
            through the actual integer values and the method won't complain.
            However, this is strongly discouraged.

        **Args:**
            *value*: the agent.status value to transpose

        **Returns**:
            The transposed agent.status value or None otherwise

        """
        log.debug('Sanitising agent.status "%s" ...' % value)
        agent_status = value

        if agent_status is not None:
            try:
                agent_status = int(agent_status)
            except ValueError, err:
                if (agent_status.lower() == 'no' or
                    agent_status.lower() == 'inactive'):
                    agent_status = 0
                elif (agent_status.lower() == 'yes' or
                      agent_status.lower() == 'active'):
                    agent_status = 1
                elif (agent_status.lower() == 'test'):
                    agent_status = 2

        log.debug('agent.status "%s" conversion produced "%s"' %
                  (value, agent_status))

        return agent_status

    def sanitise_agent_parcel_size_code(self, value):
        """Prepares the ``agent.parcel_size_code`` value for further table
        column adjustment.

        ``agent.parcel_size_code`` stores its value as a charcter value that
        directly relates to the agent ``parcel_size.code`` column.  The
        supported ``parcel_size.code`` values are "L" for large and "S"
        for standard (but is standard bigger than large ??? -- anyway).

        *value* will be taken literally if it is a case-insensitive
        "S" or "L" (converted to upper case if required).  If *value*
        is neither case-insensitive "S", "L" or ``None`` then it will
        default to "S"

        **Args:**
            *value*: the agent.parcel_size_code value to transpose

        **Returns**:
            The transposed agent.parcel_size_code value or "S" on failure

        """
        log.debug('Sanitising agent.parcel_size_code "%s" ...' % value)
        ag_parcel_size_code = value

        if (ag_parcel_size_code is None or
            not len(ag_parcel_size_code)):
            log.info('agent.parcel_size_code missing. Setting to "S"')
            ag_parcel_size_code = 'S'
        elif (ag_parcel_size_code.upper() != 'S' and
              ag_parcel_size_code.upper() != 'L'):
            log.info('%s value "%s" unknown. Setting to "S"' %
                     ('agent.parcel_size_code', ag_parcel_size_code))
            ag_parcel_size_code = 'S'
        else:
            log.info('agent.parcel_size_code set to "%s"' %
                     ag_parcel_size_code)
            ag_parcel_size_code = ag_parcel_size_code.upper()

        return ag_parcel_size_code

    def filter_update_fields(self, values, key=None):
        """Remove keys from *values* dictionary if the value meet the
        following criteria:

        * is not ``None``

        * is not an empty string

        If *key* is provided, will further filter the dictionary keys to
        those key values that match

        **Args:**
            *values*: key, value pair (dictionary) data structure that is
            to be filtered

        **Kwargs:**
            *key*: filter the dictionary against *key*

        **Returns:**
            the filtered key, value pairs

        """
        filtered_values = {}

        for k, v in values.iteritems():
            if v is not None and len(v):
                if key is None:
                    filtered_values[k] = v
                elif key == k.split('.')[0]:
                    filtered_values[k] = v

        return filtered_values

    def sanitise_delivery_partner_id(self, value):
        """Converts the string *value* to the equivalent
        ``delivery_partner.id`` value for further table column adjustment.

        ``delivery_partner.id`` is a foreign key to the ``agent.dp_id``
        column.  The ``delivery_partner`` table itself is a simple lookup.

        *value* must the Delivery Partner name as identified by the
        ``delivery_partner.name`` table column.  For example, *Nparcel*,
        *ParcelPoint*, *Toll* or *Woolworths*.

        **Args:**
            *value*: the ``delivery_partner.name`` value to transpose

        **Returns**:
            The transposed agent.parcel_size_code value or "S" on failure

        """
        log.debug('Sanitising delivery_partner.id "%s" ...' % value)
        dp_id = value

        index = None
        try:
            index = self.delivery_partners.index(dp_id) + 1
            log.debug('Found "%s" value index at %d' % (dp_id, index))
        except ValueError, err:
            log.error('"%s" lookup failed' % dp_id)

        return index

    def sanitise_login_account_status(self, value):
        """Prepares the login_account.status value for further table column
        adjustment.

        ``login_account.status`` stores its value as an integer value as
        per:

        * ``0`` for *no/inactive*
        * ``1`` for *yes/active*


        * *no/inactive* is transposed to the integer value 0

        * *yes/active* is transposed to the integer value 1

        **Args:**
            *value*: the login_account.status value to transpose

        **Returns**:
            The transposed login_account.status value or None otherwise

        """
        log.debug('Sanitising login_account.status "%s" ...' % value)
        la_status = value

        if la_status is not None:
            try:
                la_status = int(la_status)
            except ValueError, err:
                if (la_status.lower() == 'no' or
                    la_status.lower() == 'inactive' or
                    la_status.lower() == 'n'):
                    la_status = 0
                elif (la_status.lower() == 'yes' or
                      la_status.lower() == 'active' or
                      la_status.lower() == 'y'):
                    la_status = 1
        else:
            # Enable by default.
            la_status = 1

        log.debug('login_account.status: "%s" conversion produced: %d' %
                  (value, la_status))

        return la_status
