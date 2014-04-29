__all__ = [
    "Loader",
]
import re
import inspect

import top
from top.utils.log import log
from top.postcode import translate_postcode

FIELDS = {'Conn Note': {'offset': 0,
                        'length': 20},
          'Identifier': {'offset': 22,
                         'length': 19},
          'Consumer Name': {'offset': 41,
                            'length': 30},
          'Consumer Address 1': {'offset': 81,
                                 'length': 30},
          'Consumer Address 2': {'offset': 111,
                                 'length': 30},
          'Suburb': {'offset': 141,
                     'length': 30},
          'Post code': {'offset': 171,
                        'length': 6},
          'state': {'offset': 171,
                    'length': 6},
          'Bar code': {'offset': 438,
                       'length': 15},
          'Agent Id': {'offset': 453,
                       'length': 4},
          'Pieces': {'offset': 588,
                     'length': 5},
          'Email Address': {'offset': 765,
                            'length': 60},
          'Mobile Number': {'offset': 825,
                            'length': 10},
          'Service Code': {'offset': 842,
                           'length': 1},
          'Item Number': {'offset': 887,
                          'length': 32}}
JOB_MAP = {'Agent Id': {
               'column': 'agent_id',
               'required': True,
               'callback': 'get_agent_id'},
           'Bar code': {
               'column': 'card_ref_nbr',
               'required': True},
           'bu_id': {
               'column': 'bu_id',
               'required': True},
           'Consumer Address 1': {
               'column': 'address_1'},
           'Consumer Address 2': {
               'column': 'address_2'},
           'Suburb': {
               'column': 'suburb'},
           'Post code': {
               'column': 'postcode'},
           'state': {
               'column': 'state',
               'callback': translate_postcode},
           'status': {
               'column': 'status',
               'required': True,
               'default': 1},
           'job_ts': {
               'column': 'job_ts',
               'required': True},
           'Service Code': {
               'column': 'service_code',
               'callback': 'translate_service_code'}}
JOB_ITEM_MAP = {'Conn Note': {
                    'column': 'connote_nbr',
                    'required': True},
                'Item Number': {
                    'column': 'item_nbr',
                    'default_equal': 'Conn Note',
                    'required': True},
                'Consumer Name': {
                    'column': 'consumer_name'},
                'Email Address': {
                    'column': 'email_addr'},
                'Mobile Number': {
                    'column': 'phone_nbr'},
                'Pieces': {
                    'column': 'pieces'},
                'status': {
                    'column': 'status',
                    'required': True,
                    'default': 1},
                'created_ts': {
                    'column': 'created_ts',
                    'required': True,
                    'callback': 'date_now'}}


class Loader(top.Service):
    """:class:`top.Loader` object structure.
    """

    def __init__(self, db=None, comms_dir=None):
        """:class:`top.Loader` initialiser.

        """
        top.Service.__init__(self, db=db, comms_dir=comms_dir)

        self.parser = top.Parser(fields=FIELDS)

    def process(self,
                time,
                raw_record,
                bu_id,
                cond_map,
                delivery_partners=None,
                dry=False):
        """Extracts, validates and inserts/updates a TPP record.

        **Args:**
            *time*: as identified by the input file timestamp

            *raw_record*: raw record directly from a T1250 file.

            *bu_id*: the Business Unit id as per "business_unit.id"

            *cond_map*: dict representing all of the condition flags for
            the Business Unit

        **Kwargs:**
            *delivery_partners*: list of strings that represent the
            delivery partners for which comms are to be sent

            *dry*: only report, do not execute

        **Returns:**
            boolean ``True`` if processing was successful

            boolean ``False`` if processing failed

            ``None`` if an *other* scenario (typically a record ignore)

        """
        status = True

        if delivery_partners is None:
            delivery_partners = []

        # Parse the raw record and set the job timestamp.
        connote_literal = raw_record[0:20].rstrip()
        log.info('Conn Note: "%s" start parse ...' % connote_literal)
        fields = self.parser.parse_line(raw_record)

        fields['job_ts'] = time
        fields['bu_id'] = bu_id

        # Make note of the raw agent code as this is overwritten
        # during the table_column_map().
        agent_code = fields.get('Agent Id')

        barcode = fields.get('Bar code')
        log.info('Barcode "%s" start mapping ...' % barcode)
        try:
            job_data = self.table_column_map(fields,
                                             JOB_MAP,
                                             cond_map)
            job_item_data = self.table_column_map(fields,
                                                  JOB_ITEM_MAP,
                                                  cond_map)
            log.info('Barcode "%s" mapping OK' % barcode)
        except ValueError, e:
            status = False
            self.set_alerts('Barcode "%s" mapping error: %s' % (barcode, e))

        # Check for a manufactured barcode.
        if status:
            job_id = None
            skip_jobitem_chk = False

            connote = job_item_data.get('connote_nbr')
            if self.match_connote(connote, barcode):
                # Manufactured barcode.
                item_nbr = fields.get('Item Number')
                job_id = self.get_jobitem_based_job_id(connote=connote,
                                                       item_nbr=item_nbr)
                if job_id is not None:
                    skip_jobitem_chk = True
            else:
                # Explicit barcode.
                barcodes = self.barcode_exists(barcode=barcode)
                if barcodes:
                    job_id = barcodes[0]

            # OK, update or create ...
            agent_id = fields.get('Agent Id')
            agent_id_row_id = job_data.get('agent_id')
            job_item_id = None
            if job_id is not None:
                log.info('Updating barcode "%s" agent ID "%s"' %
                            (barcode, agent_id))
                job_item_id = self.update(job_id,
                                          agent_id_row_id,
                                          job_item_data,
                                          skip_jobitem_chk)
            else:
                log.info('Creating job/job_item for barcode "%s"' % barcode)
                job_item_id = self.create(job_data, job_item_data)

            # Does BU's Delivery Partner trigger comms?
            args = [agent_id, delivery_partners]
            dp_trigger_comms = self.delivery_partner_comms_trigger(*args)

            # Send comms?
            if not dp_trigger_comms:
                log.info('Agent ID %d Delivery Partner comms suppressed' %
                         (agent_id))
            else:
                if job_item_id is not None:
                    service_code = job_data.get('service_code')
                    email_addr = job_item_data.get('email_addr')
                    phone_nbr = job_item_data.get('phone_nbr')

                    self.send_comms(job_item_id,
                                    cond_map,
                                    service_code,
                                    email_addr,
                                    phone_nbr,
                                    dry=dry)

        log.info('Conn Note: "%s" parse complete' % connote_literal)

        return status

    def delivery_partner_comms_trigger(self, agent_id, delivery_partners):
        """Helper method to check whether the current Agent's Delivery
        Partner and Business Unit are configured to trigger comms.

        **Args:**
            *agent_id*: Agent ID as per the ``agent.id`` column value

            *delivery_partners*: list of strings that represent the
            delivery partners for which comms are to be sent

        """
        trigger_comms = False

        if not len(delivery_partners):
            log.debug('delivery_partners list empty')
            trigger_comms = True
        else:
            # Get the Agent's Delivery Partner.
            agent_dp = self.get_agent_delivery_partner(agent_id)

            # Match against the list of delivery_partners.
            if agent_dp in delivery_partners:
                trigger_comms = True

        log.debug('Agent ID %d delivery Partner trigger?: "%s"' %
                  (agent_id, trigger_comms))
        return trigger_comms

    def send_comms(self,
                   job_item_id,
                   cond_map,
                   service_code,
                   email_addr,
                   phone_nbr,
                   dry=False):
        """
        """
        send_sc_1 = cond_map.get('send_sc_1')
        send_sc_2 = cond_map.get('send_sc_2')
        send_sc_4 = cond_map.get('send_sc_4')
        ignore_sc_4 = cond_map.get('ignore_sc_4')
        delay_template_sc_2 = cond_map.get('delay_template_sc_2')
        delay_template_sc_4 = cond_map.get('delay_template_sc_4')

        if self.trigger_comms(service_code,
                              cond_map.get('send_email'),
                              send_sc_1,
                              send_sc_2,
                              send_sc_4,
                              ignore_sc_4):
            template = self.get_template(service_code,
                                         delay_template_sc_2,
                                         delay_template_sc_4)
            self.comms('email',
                        job_item_id,
                        email_addr,
                        template=template,
                        dry=dry)

        if self.trigger_comms(service_code,
                              cond_map.get('send_sms'),
                              send_sc_1,
                              send_sc_2,
                              send_sc_4,
                              ignore_sc_4):
            template = self.get_template(service_code,
                                         delay_template_sc_2,
                                         delay_template_sc_4)
            self.comms('sms',
                        job_item_id,
                        phone_nbr,
                        template=template,
                        dry=dry)

    def trigger_comms(self,
                      service_code,
                      send_flag,
                      send_sc_1=False,
                      send_sc_2=False,
                      send_sc_4=False,
                      ignore_sc_4=False):
        """Algorithm-based check to determine if this loader scenario
        is to trigger a comms event.

        .. note::

            Comms are not triggered if the *service_code* is ``3`` or
            the *service_code* is 4 *and* *ignore_sc_4* is ``True``.

        Default scenario if comms are enabled is that the service code
        field is NULL (or ``None``).  In this case comms are triggered
        (return ``True``).  However, certain flags can override this
        behaviour as follows:

        * ``send_sc_1`` flag is ``True`` or ``send_sc_2`` flag is ``True``

        In general, if the ``send_sc_1`` or ``send_sc_2`` flags are set
        then the default scenario is overridden.

        **Args:**
            *service_code*: integer value as per the ``job.service_code``
            column

            *cond_map*: dictionary representing all of the condition flags
            for the Business Unit

            *send_sc_1*: flag to trigger comms if the *service_code*
            is equal to ``1``

            *send_sc_2*: flag to trigger comms if the *service_code*
            is equal to ``2``

            *ignore_sc_4*: flag to ignore records if the *service_code*
            is equal to ``4``

        **Returns:**
            boolean ``True`` if comms should be sent

            boolean ``False`` otherwise

        """
        log.info('Comms trigger check SC:%s - SC_1|SC_2|SC_4: %s|%s|%s' %
                 (service_code, send_sc_1, send_sc_2, send_sc_4))
        prepare_comms = False

        if send_flag:
            if service_code == 3:
                log.info('Not setting comms for Service Code 3')
            elif service_code == 4 and ignore_sc_4:
                log.info('Not setting comms for Service Code 4')
            else:
                if not send_sc_1 and not send_sc_2 and not send_sc_4:
                    prepare_comms = True
                else:
                    if ((service_code == 1 and send_sc_1) or
                        (service_code == 2 and send_sc_2) or
                        (service_code == 4 and send_sc_4)):
                        log.info('Setting comms for Service Code %s' %
                                 str(service_code))
                        prepare_comms = True
        else:
            log.info('Comms facility disabled')

        return prepare_comms

    def comms(self,
              method,
              job_item_id,
              recipient,
              template='body',
              dry=False):
        """Prepare comms event files.

        **Args:**
            *job_item_id*: integer as per the ``job_item.id`` column

            *recipient*: comms email recipient address

            *method*: either ``email`` or ``sms``

            *dry*: only report, do not execute

        """
        log.info('Checking comms for id|recipient|method: %s|%s|%s' %
                 (job_item_id, recipient, method))

        if recipient is not None and recipient:
            self.flag_comms(method,
                            job_item_id,
                            template,
                            dry=dry)

    def get_agent_details(self, agent_id):
        """Get agent details.

        **Args:**
            agent_id: as per the agent.id table column

        **Returns:**
            dictionary structure capturing the Agent's details similar to::

                {'name': 'Vermont South Newsagency',
                 'address': 'Shop 13-14; 495 Burwood Highway',
                 'suburb': 'VERMONT',
                 'postcode': '3133'}

        """
        agent_details = {}

        self.db(self.db._agent.agent_sql(id=agent_id))
        agent_row = self.db.row
        if agent_row is not None:
            (name, address, suburb, postcode) = agent_row
            agent_details = {'name': name,
                             'address': address,
                             'suburb': suburb,
                             'postcode': postcode}
        else:
            err = 'Comms missing Agent for id: %d' % agent_id
            log.error(err)

        return agent_details

    def barcode_exists(self, barcode):
        """
        """
        barcode_list = []

        log.info('Checking if barcode "%s" exists in "job" table ...' %
                 barcode)
        self.db(self.db._job.check_barcode(barcode=barcode))

        for row in self.db.rows():
            barcode_list.append(row[0])

        log.info('"job" records with barcode "%s": %s' %
                 (barcode, str(barcode_list)))

        return barcode_list

    def get_agent_id(self, agent):
        """Helper method to verify if an Agent ID is defined.

        **Args:**
            *agent*: the raw agent string (for example, ``N001``)

        **Returns:**
            on success, integer value taken from ``agent.id`` representing
            the *agent* details.  ``None`` otherwise.

        """
        log.info('Checking if Agent Id "%s" exists in system ...' % agent)
        self.db(self.db._agent.check_agent_id(agent_code=agent))
        agent_id_row_id = self.db.row

        if agent_id_row_id is not None:
            agent_id_row_id = agent_id_row_id[0]
            log.info('Agent Id "%s" found: %s' % (agent, agent_id_row_id))
        else:
            self.set_alerts('Agent Id "%s" does not exist' % agent)

            # For testing only, create the record.
            # First insert will fail the test -- subsequent checks should
            # be OK.  This will ensure we get a mix during testing.
            if self.db.host is None:
                log.debug('TEST: Creating Agent Id "%s" record ...' % agent)
                agent_fields = {'code': agent}
                sql = self.db._agent.insert_sql(agent_fields)
                # Just consume the new row id.
                id = self.db.insert(sql)

        return agent_id_row_id

    def get_agent_delivery_partner(self, agent_id):
        """Helper method to retrieve an Agent ID's Delivery Partner.

        **Args:**
            *agent_id*: the raw agent ID (as per the ``agent.id`` table
            column)

        **Returns:**
            on success, string representation of the Agent's Delivery
            Partner (as per the ``delivery_partner.name`` column.
            ``None`` otherwise

        """
        log.info('Get agent.id %d Delivery Partner ...' % agent_id)
        sql = self.db._agent.agent_sql(agent_id)

        self.db(sql)
        columns = self.db.columns()
        index = None
        try:
            index = columns.index('DP_NAME')
        except ValueError, err:
            log.error('Unable to find DP_NAME column in query results')

        dp = None
        if index is not None:
            try:
                dp = self.db.row[index]
            except TypeError, err:
                log.error('Unable to extract DP_NAME from agent table: %s' %
                          err)

        log.info('agent.id %d Delivery Partner: "%s"' % (agent_id, dp))

        return dp

    def table_column_map(self, fields, map, condition_map):
        """Convert the parser fields to Toll Outlet Portal table column
        names in preparation for table manipulation.

        **Args:**
            fields: dictionary of :class:`top.Parser` fields and
            values.

            map: dictionary of :class:`top.Parser` fields to table
            columns.

        **Returns:**
            dictionary of table columns and values in the form::

                {'<column_1>': '<value>',
                 '<column_2>': '<value>'
                 ...}

        **Raises:**
            ValueError if all *fields* cannot be mapped.

        """
        self.set_callbacks(fields, map)
        self.set_defaults(fields, map)
        self.set_default_equals(fields,
                                map,
                                condition_map.get('item_number_excp'))
        return self.set_columns(fields, map)

    def set_callbacks(self, fields, map):
        """Process column map callbacks.

        For each parsed field, check if a the mapping defines a 'callback'
        option.  If so, it will process the existing field value
        according to the logic defined in the callback.

        **Args:**
            as per :meth:`table_column_map`

        """
        for field_name, v in map.iteritems():
            if v.get('callback'):
                # Check if the callback is a function or string.
                if inspect.isroutine(v.get('callback')):
                    callback = v.get('callback')
                else:
                    callback = getattr(self, v.get('callback'))

                log.debug('Executing "%s" callback: "%s" ...' %
                          (field_name, v.get('callback')))
                fields[field_name] = callback(fields.get(field_name))

    def set_defaults(self, fields, map):
        """Process column defaults.

        Cycles through each raw, parsed fields and checks if the 'default'
        option is set.  Will only assign the default if the current
        field value is empty.

        **Args:**
            as per :meth:`table_column_map`

        """
        for field_name, v in map.iteritems():
            if not fields.get(field_name):
                if v.get('default') is not None:
                    fields[field_name] = v.get('default')
                    log.debug('Set default value "%s" to "%s"' %
                              (v.get('default'), field_name))

    def set_default_equals(self, fields, map, item_number_excp):
        """Process column default equals.

        Cycles through each raw, parsed fields and checks if the
        'default_equals' option is set.  Will only assign the default_equals
        if the current field value is empty.

        **Args:**
            *fields* and *map* as per :meth:`table_column_map`

            item_number_excp: boolean flag which controls whether a
            missing "Item Number" raises an exception (if set to ``True``)

        """
        for field_name, v in map.iteritems():
            if (not fields.get(field_name) and
                (field_name == 'Item Number' and item_number_excp)):
                log.debug('Missing Item number set to raise exception')
                continue

            if not fields.get(field_name):
                if v.get('default_equal') is not None:
                    copy_value = fields.get(v.get('default_equal'))
                    fields[field_name] = copy_value
                    log.debug('Set default_equal value "%s:%s" to "%s"' %
                              (v.get('default_equal'),
                               copy_value,
                               field_name))

    def set_columns(self, fields, map):
        """Performs the actual mapping between the raw, parser fields and
        the table columns.

        Also runs a preliminary check to ensure that empty fields set as
        "required" raise an exception.

        **Args:**
            as per :meth:`table_column_map`

        **Returns:**
            as per :meth:`table_column_map`

        """
        for field_name, v in map.iteritems():
            if v.get('required') and not fields.get(field_name):
                raise ValueError('Field "%s" is required' % field_name)

        cols = dict((map.get(k).get('column'),
                        fields.get(k)) for (k, v) in map.iteritems())

        return cols

    def translate_service_code(self, service_code):
        """Translate postcode information to state.

        **Args:**
            *service_code*: raw Service Code value.  In the case of primary,
            elect it is the character '3'.

        **Returns:**
            integer representation of the raw Service Code, or ``None``
            if an error condition is encountered.

        """
        log.debug('Translating raw Service Code value: "%s" ...' %
                  service_code)

        translated_sc = 'NULL'
        if service_code and service_code is not None:
            try:
                translated_sc = int(service_code)
                log.debug('Service code translated to %d' % translated_sc)
            except (TypeError, ValueError), e:
                log.warn('Unable to translate Service Code "%s": %s' %
                         (service_code, e))

        return translated_sc

    def date_now(self, *args):
        """
        """
        return self.db.date_now()

    def reset(self, commit=False):
        """Reset the alert list.
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

    def match_connote(self, connote, barcode):
        """Pre-check to see if barcode value is based on connote.

        This special condition occurs when operators cannot record parcel
        against a missing barcode.  Instead, a barcode value is manufactured
        from the existing connote.  Due to system limitations, the
        manufactured connote is truncated in the system.  This loss of
        precision introduces the chance of false-positives during the
        barcode comparison phase.

        **Args:**
            connote: connote value parsed directly from the T1250 file

            barcode: barcode value parsed directly from the T1250 file

        **Returns:**
            boolean True if barcode is manufactured against connote

            boolean False otherwise

        """
        match = False

        if len(connote) > 15:
            log.debug('Connote "%s" length is greater than 15' % connote)
            # Check barcode position 1 to 15.
            for tmp_barcode in [barcode[:16], barcode[4:16]]:
                log.debug('Manufactured barcode to check: "%s"' %
                          tmp_barcode)
                m = re.search(tmp_barcode, connote)
                if m is not None:
                    match = True
                    log.info('Ambiguous connote/barcode "%s/%s"' %
                            (connote, barcode))
                    break

        return match

    def get_jobitem_based_job_id(self, connote, item_nbr):
        """Checks the "job" table for related "job_item" records with
        *connote* and *item_nbr*.  If more than one job exists, will sort
        against the job_ts against the most recent record.

        **Args:**
            connote: connote value parsed directly from the T1250 file

            item_nbr: item_nbr value parsed directly from the T1250 file

        **Returns:**
            integer value relating to the job.id if match is found.

            ``None`` otherwise.

        """
        log.info('Check for job records with connote/item_nbr: "%s"/"%s"' %
                 (connote, item_nbr))
        job_id = None

        sql = self.db.job.jobitem_based_job_search_sql(connote=connote,
                                                       item_nbr=item_nbr)
        self.db(sql)
        received = []
        for row in self.db.rows():
            received.append(row[0])

        if received:
            # Results are sorted by job_ts so grab the first index.
            job_id = received[0]
            log.info('Item Number check -- job record id %d found' % job_id)

        return job_id

    def get_item_number_job_id(self, item_nbr):
        """Checks the "job" table for related "job_item" records with
        *item_nbr*.  If more than one job exists, will sort against the
        job_ts against the most recent record.

        **Args:**
            item_nbr: item_nbr value parsed directly from the T1250 file

        **Returns:**
            integer value relating to the job.id if match is found.

            ``None`` otherwise.

        """
        log.info('Check for job records with item_nbr "%s"' % item_nbr)
        job_id = None

        sql = self.db.job.item_nbr_based_job_sql(item_nbr=item_nbr)
        self.db(sql)
        received = []
        for row in self.db.rows():
            received.append(row[0])

        if received:
            # Results are sorted by job_ts so grab the first index.
            job_id = received[0]
            log.info('Connote check -- job record id %d found' % job_id)

        return job_id

    def create(self, job_data, jobitem_data):
        """
        **Args:**
            *job_data*: dictionary of the ``job`` table fields

            *jobitem_data*: dictionary of the ``jobitem`` table fields

        **Returns:**
            integer representing the new ``job_item.id``

        """
        job_id = self.db.insert(self.db.job.insert_sql(job_data))
        log.info('"job.id" %d created' % job_id)

        # Set the "jobitem" table's foreign key.
        jobitem_data['job_id'] = job_id
        sql = self.db.jobitem.insert_sql(jobitem_data)
        jobitem_id = self.db.insert(sql)
        log.info('"jobitem.id" %d created' % jobitem_id)

        return jobitem_id

    def update(self,
               job_id,
               agent_id,
               jobitem_data,
               skip_jobitem_chk=False):
        """Updates and existing barcode.

        Updates the job.agent_id and will create a new job_item.connote_nbr
        if the connote does not already exist in the job_item table.

        **Args:**
            job_id: row ID of the "job" table

            agent_id: row ID of the "agent" table

            jobitem_data: dictionary of the "jobitem" table fields

            skip_jobitem_chk: bypass jobitem insert check and only update
            the job record (default ``False``)

        **Returns:**
            integer representing the new ``job_item.id``

        """
        job_item_id = None

        sql = self.db.job.update_sql(job_id, agent_id)
        self.db(sql)

        if not skip_jobitem_chk:
            connote = jobitem_data.get('connote_nbr')
            item_nbr = jobitem_data.get('item_nbr')
            log.debug('Look for jobitems with connote/item_nbr: "%s"/"%s"' %
                      (connote, item_nbr))
            sql = self.db.jobitem.connote_item_nbr_sql(connote, item_nbr)
            job_item_ids = []
            self.db(sql)
            for row in self.db.rows():
                job_item_ids.append(row[0])

            if not job_item_ids:
                # Set the "jobitem" table's foreign key.
                jobitem_data['job_id'] = job_id
                sql = self.db.jobitem.insert_sql(jobitem_data)
                job_item_id = self.db.insert(sql)
                log.info('"jobitem.id" %d created' % job_item_id)
            else:
                log.info('"jobitem.id" %d exists' % job_item_ids[0])
                job_item_id = job_item_ids[0]
        else:
            log.debug('Skipping jobitems check')

        return job_item_id

    def verify_postcodes(self, dry=False):
        """Cycle through each ``job.state`` column and enusure that the
        ``job.postcode`` evaluates as expected.

        Unless a *dry* run is specified, it will attempt to update the
        ``job.state`` in line with the ``job.postcode`` state evaluation.

        **Kwargs:**
            *dry*: only report, do not execute

        """
        log.info('Extracting existing job.states ...')
        sql = self.db.job.postcode_sql()
        self.db(sql)

        for row in self.db.rows():
            # Comes through as id, postcode, state.
            log.debug('Verifying job.id: %d ...' % row[0])
            translated_state = translate_postcode(row[1])
            m = re.match(translated_state, row[2])
            if m is None:
                log.info('job.id %d postcode "%s" has wrong state "%s"' %
                         (row[0], row[1], row[2]))
                log.info('Updating job.id: %d to state "%s"' %
                         (row[0], translated_state))
                sql = self.db.job.update_postcode_sql(row[0],
                                                      translated_state)
                self.db(sql)
                if not dry:
                    self.db.commit()
            else:
                log.debug('job.id %d OK' % row[0])

    def ignore_record(self, agent_code):
        """Manages Business Unit rules that determine if a raw T1250
        record should be ignored.

        Current ignore rules include:

        * *Agent Id* starts with a ``P`` (this indicates a ParcelPoint job)

        **Args:**
            *agent_code*: the raw agent code string as parsed from the
            T1250 file.  For example:: ``N013``.

        **Returns:**
            boolean ``True`` if record should be ignored

            boolean ``False`` otherwise

        """
        log.info('Checking ignore rules ...')
        ignore = False

        log.debug('Checking agent code "%s"' % agent_code)
        if agent_code is not None:
            if agent_code.startswith('P'):
                log.info('Agent code "%s" starts with "P" -- ignoring' %
                         agent_code)
                ignore = True

        return ignore

    def get_template(self,
                     service_code,
                     delay_template_sc_2,
                     delay_template_sc_4):
        """Determine which template to use.

        In addition to the standard notification template, the Loader
        facility could trigger comms based on an alternate template
        construct.

        Current alternate templates supported include:

        * **delay** - for delayed pickup notifications.  Triggered with
          *service_code* ``2`` and *delay_template_sc_2* is ``True`` or
          *service_code* ``4`` and *delay_template_sc_4* is ``True``

        **Args:**
            *service_code*: raw Service Code value as taken from
            ``job.service_code`` column

        **Returns:**
            string name of the template.  Currently can be one of:

            * ``body`` -- standard comms notification

            * ``delay`` -- delayed pickup notifications

        """
        log.info('Getting template for service_code value: %s' %
                 str(service_code))
        template = 'body'

        if service_code is not None:
            if ((service_code == 2 and delay_template_sc_2) or
                (service_code == 4 and delay_template_sc_4)):
                template = 'delay'

        msg = ('Template for SC with flag delay_sc2|delay_sc4 %s|%s: %s' %
               (delay_template_sc_2, delay_template_sc_4, template))
        log.debug(msg)

        return template
