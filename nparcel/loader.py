__all__ = [
    "Loader",
]
import re
import inspect

import nparcel
from nparcel.utils.log import log

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
               'callback': 'translate_postcode'},
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
POSTCODE_MAP = {'NSW': {
                    'ranges': [
                        (1000, 1999),
                        (2000, 2599),
                        (2619, 2898),
                        (2921, 2999)],
                    'exceptions': [
                         2899]},
                'ACT': {
                    'ranges': [
                        (200, 299),
                        (2600, 2618),
                        (2900, 2920)],
                    'exceptions': []},
                'VIC': {
                    'ranges': [
                        (3000, 3999),
                        (8000, 8999)],
                    'exceptions': []},
                'QLD': {
                    'ranges': [
                        (4000, 4999),
                        (9000, 9999)],
                    'exceptions': []},
                'SA': {
                    'ranges': [
                        (5000, 5799),
                        (5800, 5999)],
                    'exceptions': []},
                'WA': {
                    'ranges': [
                        (6000, 6797),
                        (6800, 6999)],
                    'exceptions': []},
                'TAS': {
                    'ranges': [
                        (7000, 7999)],
                    'exceptions': []},
                'NT': {
                    'ranges': [
                        (800, 999)],
                    'exceptions': []}}


class Loader(nparcel.Service):
    """Nparcel Loader object.

    """

    def __init__(self, db=None, comms_dir=None):
        """Nparcel Loader initialiser.

        """
        super(nparcel.Loader, self).__init__(db=db, comms_dir=comms_dir)

        self.parser = nparcel.Parser(fields=FIELDS)
        self.alerts = []

    def process(self, time, raw_record, bu_id, cond_map, dry=False):
        """Extracts, validates and inserts/updates an Nparcel record.

        **Args:**
            *time*: as identified by the input file timestamp

            *raw_record*: raw record directly from a T1250 file.

            *bu_id*: the Business Unit id as per "business_unit.id"

            *conditions*: dict representing all of the condition flags for
            the Business Unit

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            boolean ``True`` if processing was successful

            boolean ``False`` if processing failed

        """
        status = True

        # Parse the raw record and set the job timestamp.
        connote_literal = raw_record[0:20].rstrip()
        log.info('Conn Note: "%s" start parse ...' % connote_literal)
        fields = self.parser.parse_line(raw_record)
        fields['job_ts'] = time
        fields['bu_id'] = bu_id

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
            self.set_alert('Barcode "%s" mapping error: %s' % (barcode, e))

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
                log.info('Updating Nparcel barcode "%s" agent ID "%s"' %
                         (barcode, agent_id))
                job_item_id = self.update(job_id,
                                          agent_id_row_id,
                                          job_item_data,
                                          skip_jobitem_chk)
            else:
                log.info('Creating Nparcel barcode "%s"' % barcode)
                job_item_id = self.create(job_data, job_item_data)

            send_email = cond_map.get('send_email')
            send_sms = cond_map.get('send_sms')
            if job_item_id is not None:
                if send_email:
                    self.flag_comms('email', job_item_id, 'body', dry=dry)
                if send_sms:
                    self.flag_comms('sms', job_item_id, 'body', dry=dry)
            else:
                log.info('Not setting comms flag for job_item_id %s' %
                         str(job_item_id))

        log.info('Conn Note: "%s" parse complete' % connote_literal)

        return status

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
        """
        log.info('Checking if Agent Id "%s" exists in system ...' % agent)
        self.db(self.db._agent.check_agent_id(agent_code=agent))
        agent_id_row_id = self.db.row

        if agent_id_row_id is not None:
            agent_id_row_id = agent_id_row_id[0]
            log.info('Agent Id "%s" found: %s' % (agent, agent_id_row_id))
        else:
            err = 'Agent Id "%s" does not exist' % agent
            self.set_alert(err)

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

    def table_column_map(self, fields, map, condition_map):
        """Convert the parser fields to Nparcel table column names in
        preparation for table manipulation.

        **Args:**
            fields: dictionary of :class:`nparcel.Parser` fields and
            values.

            map: dictionary of :class:`nparcel.Parser` fields to table
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

    def translate_postcode(self, postcode):
        """Translate postcode information to state.

        **Args:**
            *postcode*: integer representing a postcode (for example, 3754)

        **Returns:**
            string representing the state of the translated postcode

        """
        log.debug('Translating raw postcode value: "%s" ...' % postcode)

        state = ''
        try:
            postcode = int(postcode)
        except ValueError, e:
            log.warn('Unable to translate postcode "%s"' % postcode)

        if isinstance(postcode, int):
            for postcode_state, postcode_ranges in POSTCODE_MAP.iteritems():
                for range in postcode_ranges.get('ranges'):
                    if postcode >= range[0] and postcode <= range[1]:
                        state = postcode_state
                        break
                for exception in postcode_ranges.get('exceptions'):
                    if postcode == exception:
                        state = postcode_state
                        break

                if state:
                    break

            log.debug('Postcode/state - %d/"%s"' % (postcode, state))

        return state

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

    def set_alert(self, alert):
        log.error(alert)
        self.alerts.append(alert)

    def reset(self, commit=False):
        """Reset the alert list.
        """
        del self.alerts[:]

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
