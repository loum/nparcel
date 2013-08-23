__all__ = [
    "Loader",
]
import re

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
               'required': True}}
JOB_ITEM_MAP = {'Conn Note': {
                    'column': 'connote_nbr'},
                'Item Number': {
                    'column': 'item_nbr',
                    'default_equal': 'Conn Note',
                    'required': True},
                'Consumer Name': {
                    'column': 'consumer_name'},
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
                    'ranges': [],
                    'exceptions': []},
                'WA': {
                    'ranges': [
                        (5000, 5999)],
                    'exceptions': []},
                'TAS': {
                    'ranges': [
                        (7000, 7999)],
                    'exceptions': []},
                'NT': {
                    'ranges': [
                        (800, 999)],
                    'exceptions': []}}


class Loader(object):
    """Nparcel Loader object.

    .. attributes:: db

        :class:`nparcel.DbSession` object

    """

    def __init__(self, db=None):
        """Nparcel Loader initaliser.

        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self.parser = nparcel.Parser(fields=FIELDS)
        self.alerts = []

        self.emailer = nparcel.Emailer()
        self.smser = nparcel.Smser()

    def process(self,
                time,
                raw_record,
                bu_id,
                email=None,
                sms=None,
                dry=False):
        """Extracts, validates and inserts/updates an Nparcel record.

        **Args:**
            time: as identified by the input file timestamp

            raw_record: raw record directly from a T1250 file.

            bu_id: the Business Unit id as per "business_unit.id"

        **Kwargs:**
            email: list of email addresses to send to (special case)

            sms: list of numbers to SMS comms to (special case)

        **Returns:**

            boolean ``True`` if processing was successful

            boolean ``False`` if processing failed

        """
        status = True

        # Parse the raw record and set the job timestamp.
        connote = raw_record[0:20].rstrip()
        log.info('Conn Note: "%s" start parse ...' % connote)
        fields = self.parser.parse_line(raw_record)
        fields['job_ts'] = time
        fields['bu_id'] = bu_id

        barcode = fields.get('Bar code')
        log.info('Barcode "%s" start mapping ...' % barcode)

        try:
            job_data = self.table_column_map(fields, JOB_MAP)
            job_item_data = self.table_column_map(fields, JOB_ITEM_MAP)
            log.info('Barcode "%s" mapping OK' % barcode)
        except ValueError, e:
            status = False
            self.set_alert('Barcode "%s" mapping error: %s' % (barcode, e))

        # Check for a manufactured barcode (based on connote).
        if status:
            job_id = None

            if self.match_connote(connote, barcode):
                # Manufactured barcode.
                job_id = self.get_connote_job_id(connote=connote)
            else:
                # Expicit barcode.
                barcodes = self.barcode_exists(barcode=barcode)
                if barcodes:
                    job_id = barcodes[0]

            # OK, update or create ...
            agent_id = fields.get('Agent Id')
            agent_id_row_id = job_data.get('agent_id')
            if job_id is not None:
                log.info('Updating Nparcel barcode "%s" agent ID "%s"' %
                         (barcode, agent_id))
                self.update(job_id, agent_id_row_id, job_item_data)
            else:
                log.info('Creating Nparcel barcode "%s"' % barcode)
                self.create(job_data, job_item_data)

            # Send out comms.
            self.send_email(agent_id_row_id, email, barcode, dry)
            self.send_sms(agent_id_row_id, sms, barcode, dry)

        log.info('Conn Note: "%s" parse complete' % connote)

        return status

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

    def table_column_map(self, fields, map):
        """Convert the parser fields to Nparcel table column names in
        preparation for table manipulation.

        Runs a preliminary check to ensure that all requireditems in
        *fields* can be mapped.  Raises a ``ValueError`` if otherwise.

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
        columns = {}

        for field_name, v in map.iteritems():
            # Check for callbacks.
            if v.get('callback'):
                log.debug('Executing "%s" callback: "%s" ...' %
                          (field_name, v.get('callback')))
                callback = getattr(self, v.get('callback'))
                fields[field_name] = callback(fields.get(field_name))

            if not fields.get(field_name):
                if v.get('default') is not None:
                    fields[field_name] = v.get('default')

        # Map to an existing field if we are currently empty.
        for field_name, v in map.iteritems():
            if not fields.get(field_name):
                if v.get('default_equal') is not None:
                    log.debug('"%s" set to "%s" value' %
                              (field_name, v.get('default_equal')))
                    copy_value = fields.get(v.get('default_equal'))
                    fields[field_name] = copy_value

            # By now, if we don't have data and we are "required" then
            # raise an exception.
            if v.get('required') and not fields.get(field_name):
                raise ValueError('Field "%s" is required' % field_name)

        columns = dict((map.get(k).get('column'),
                        fields.get(k)) for (k, v) in map.iteritems())

        return columns

    def translate_postcode(self, postcode):
        """Translate postcode information to state.
        """
        log.debug('Translating raw postcode value: "%s" ...' % postcode)

        state = ''
        try:
            postcode = int(postcode)
        except ValueError, e:
            log.warn('Unable to convert "%s" to an integer' % postcode)

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

        This special coniditon occurs when operators cannot record parcel
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

    def get_connote_job_id(self, connote):
        """Checks the "job" table for related "job_item" records with
        *connote*.  If more than one job exists, will sort against the
        job_ts against the most recent record.

        **Args:**
            connote: connote value parsed directly from the T1250 file

        **Returns:**
            integer value relating to the job.id if match is found.

            ``None`` otherwise.

        """
        log.info('Check for job records with connote "%s"' % connote)
        job_id = None

        sql = self.db.job.connote_based_job_sql(connote=connote)
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
            job_data: dictionary of the "job" table fields

            jobitem_data: dictionary of the "jobitem" table fields

        """
        job_id = self.db.insert(self.db.job.insert_sql(job_data))
        log.info('"job.id" %d created' % job_id)

        # Set the "jobitem" table's foreign key.
        jobitem_data['job_id'] = job_id
        sql = self.db.jobitem.insert_sql(jobitem_data)
        jobitem_id = self.db.insert(sql)
        log.info('"jobitem.id" %d created' % jobitem_id)

    def update(self, job_id, agent_id, jobitem_data):
        """Updates and existing barcode.

        Updates the job.agent_id and will create a new job_item.connote_nbr
        if the connote does not already exist in the job_item table.

        **Args:**
            job_id: row ID of the "job" table

            agent_id: row ID of the "agent" table

            jobitem_data: dictionary of the "jobitem" table fields

        """
        sql = self.db.job.update_sql(job_id, agent_id)
        self.db(sql)

        connote = jobitem_data.get('connote_nbr')
        log.info('Check if connote "%s" job_item already exists' % connote)
        sql = self.db.jobitem.connote_sql(connote)
        job_item_ids = []
        self.db(sql)
        for row in self.db.rows():
            job_item_ids.append(row[0])

        if not job_item_ids:
            # Set the "jobitem" table's foreign key.
            jobitem_data['job_id'] = job_id
            sql = self.db.jobitem.insert_sql(jobitem_data)
            jobitem_id = self.db.insert(sql)
            log.info('"jobitem.id" %d created' % jobitem_id)
        else:
            log.info('"jobitem.id" %d exists' % job_item_ids[0])

    def send_email(self,
                   agent_id,
                   to_addresses,
                   barcode,
                   dry=False):
        """Send out email comms to the list of *to_addresses*.

        **Args:**
            agent_id: the Agent's "agent.id" private key

            to_addresses: list of email recipients

            barcode: job barcode

        **Kwargs:**
            dry: only report, do not actual execute

        **Returns:**
            ``True`` for processing success

            ``False`` for processing failure

        """
        status = True

        # Send out email comms.
        if to_addresses is not None and len(to_addresses):
            log.debug('Sending customer email to "%s"' % to_addresses)

            # Get agent details.
            self.db(self.db._agent.agent_sql(id=agent_id))
            agent = self.db.row
            if agent is not None:
                (name, address, suburb, postcode) = agent

                # OK, generate the email structure.
                subject = 'Nparcel pickup'
                msg = """Your consignment has been placed at %s, %s, %s %s.  Consignment Ref %s.  Please bring your photo ID with you.  Enquiries 13 32 78""" % (name, address, suburb, postcode, barcode)
                self.emailer.set_recipients(to_addresses)
                status = self.emailer.send(subject=subject,
                                           msg=msg,
                                           dry=dry)
            else:
                status = False
                log.warn('Email no Agent details for id: %d' % agent_id)
        else:
            log.warn('Email list is empty')

        return status

    def send_sms(self, agent_id, mobiles, barcode, dry=False):
        """Send out SMS comms to the list of *mobiles*.

        **Args:**
            agent_id: the Agent's "agent.id" private key

            mobiles: list of SMS recipients

            barcode: job barcode

        **Kwargs:**
            dry: only report, do not actual execute

        **Returns:**
            ``True`` for processing success

            ``False`` for processing failure

        """
        status = True

        # Send out SMS comms.
        if mobiles is not None and len(mobiles):
            log.debug('Sending customer email to "%s"' % str(mobiles))

            # Get agent details.
            self.db(self.db._agent.agent_sql(id=agent_id))
            agent = self.db.row
            if agent is not None:
                (name, address, suburb, postcode) = agent

                # OK, generate the SMS structure.
                subject = 'Nparcel pickup'
                msg = """Your consignment has been placed at %s, %s, %s %s.  Consignment Ref %s.  Please bring your photo ID with you.  Enquiries 13 32 78""" % (name, address, suburb, postcode, barcode)
                self.smser.set_recipients(mobiles)
                status = self.smser.send(msg=msg, dry=dry)
            else:
                status = False
                err = 'SMS missing Agent details for id: %d' % agent_id
                self.set_alert(err)
        else:
            log.warn('SMS list is empty')

        return status
