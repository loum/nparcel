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
                        'length': 4},
          'state': {'offset': 171,
                    'length': 4},
          'Bar code': {'offset': 438,
                       'length': 15},
          'Agent Id': {'offset': 453,
                       'length': 4},
          'Pieces': {'offset': 588,
                     'length': 5}}
JOB_MAP = {'Agent Id': {
               'column': 'agent_id',
               'required': True,
               'callback': 'get_agent_id'},
           'Bar code': {
               'column': 'card_ref_nbr',
               'required': True},
           'Identifier': {
               'column': 'bu_id',
               'required': True,
               'callback': 'translate_bu_id'},
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

    .. attribute:: file_bu

        Dictionary of tokens that identify a Business Unit and maps
        to a known database entry.
    """

    def __init__(self, file_bu, db=None):
        """
        """
        self.file_bu = file_bu

        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self.parser = nparcel.Parser(fields=FIELDS)
        self.alerts = []

    def process(self, time, raw_record):
        """
        Extracts, validates and inserts an Nparcel record.

        **Args:**
            raw_record: raw record directly from a T1250 file.

        """
        status = True

        # Parse the raw record and set the job timestamp.
        connote = raw_record[0:18].rstrip()
        log.info('Conn Note: "%s" start parse ...' % connote)
        fields = self.parser.parse_line(raw_record)
        fields['job_ts'] = time

        barcode = fields.get('Bar code')

        try:
            log.info('Barcode "%s" start mapping ...' % barcode)
            job_data = self.table_column_map(fields, JOB_MAP)
            job_item_data = self.table_column_map(fields, JOB_ITEM_MAP)
            log.info('Barcode "%s" mapping OK' % barcode)
        except ValueError, e:
            status = False
            msg = 'Barcode "%s" mapping error: %s' % (barcode, e)
            log.error(msg)
            self.set_alert(msg)

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
            if job_id is not None:
                agent_id = fields.get('Agent Id')
                log.info('Updating Nparcel barcode "%s" agent ID "%s"' %
                         (barcode, agent_id))
                agent_id_row_id = job_data.get('agent_id')
                self.update(job_id, agent_id_row_id, job_item_data)
            else:
                log.info('Creating Nparcel barcode "%s"' % barcode)
                self.create(job_data, job_item_data)

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
        self.db(self.db._agent.check_agent_id(agent_id=agent))

        agent_id_row_id = self.db.row
        if agent_id_row_id is not None:
            agent_id_row_id = agent_id_row_id[0]
            log.info('Agent Id "%s" found: %s' % (agent, agent_id_row_id))
        else:
            log.error('Agent Id "%s" does not exist' % agent)

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

        Runs a preliminary check to ensure that all items in *fields*
        can be mapped.  Raises a ``ValueError`` if otherwise.

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

            if (v.get('required') and
                not fields.get(field_name) and
                not v.get('default')):
                raise ValueError('Field "%s" is required' % field_name)

            if not fields.get(field_name):
                if v.get('default') is not None:
                    fields[field_name] = v.get('default')

        columns = dict((map.get(k).get('column'),
                        fields.get(k)) for (k, v) in map.iteritems())

        return columns

    def translate_bu_id(self, value):
        """
        """
        bu_id = None

        log.debug('Translating "%s" to BU ...' % value)
        m = re.search('YMLML11(TOL.).*', value)
        bu_id = self.file_bu.get(m.group(1).lower())

        if bu_id is None:
            log.error('Unable to extract BU from "%s"' % value)
        else:
            bu_id = int(bu_id)

        return bu_id

    def translate_postcode(self, postcode):
        """Translate postcode information to state.
        """
        log.debug('Translating postcode: "%s" ...' % str(postcode))
        state = ''

        if postcode:
            postcode = int(postcode)

            for postcode_state, postcode_ranges in POSTCODE_MAP.iteritems():
                for range in postcode_ranges.get('ranges'):
                    if postcode >= range[0] and postcode <= range[1]:
                        state = postcode_state
                        break
                for exception in  postcode_ranges.get('exceptions'):
                    if postcode == exception:
                        state = postcode_state
                        break

                if state:
                    break

        log.debug('Postcode "%s" translation produced: "%s"' %
                  (str(postcode), state))

        return state

    def date_now(self, *args):
        """
        """
        return self.db.date_now()

    def set_alert(self, alert):
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
