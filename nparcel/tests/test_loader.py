import unittest2
import datetime

import nparcel


FILE_BU = {'tolp': '1', 'tolf': '2', 'toli': '3'}
VALID_LINE_BARCODE = '4156536111'
VALID_LINE_CONNOTE = '218501217863'
VALID_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
VALID_LINE_AGENT_UPD = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N014                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N014                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
INVALID_BARCODE_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                                              N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
INVALID_AGENTID_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111                                                                                                                                            00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
INVALID_POSTCODE_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other                                                                                                                                    Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
MANUFACTURED_BC_LINE = """3142357006912345      YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other                                                                                                                                    Diane Donohoe                             Bally                         Hong Kong Other                                                               000931423570069N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
MANUFACTURED_BC_UPD_LINE = """3142357006912345      YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other                                                                                                                                    Diane Donohoe                             Bally                         Hong Kong Other                                                               000931423570069N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N032                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
SINGLE_QUOTE_LINE = """080102033141          YMLML11TOLP130815  MISS S D'ARCY                           13 FITZGERALD RD              ESSENDON                      MELBOURNE                     3040                                                                                                                 MISS S D'ARCY                             NEXT RETAIL LTD               LEICESTER                                                                     4159214753     V098                                                                                                                                   00001000001                                                                      Parcels Overnight                   DESFORD ROAD                  ENDERBY                                                                                                              FVAN000098                                                                                                 GB                            AUSTRALIA                                                                                                                                                                                                         VI                                               """
DODGY_POSTCODE = """574000244915          YMLML11TOLP130715  AMAL DOUKARI                            41 BLAMEY ST 1501 KELVIN GROVEQUEEN SLAND 4059              ;                             ;                                                                                                                    AMAL DOUKARI                              GUANGZHOU YASHUNDA LTD                                      362000                                          4159054556     Q067                                                                                                                                   00001000001                                                                      Parcels Overnight                   NO.83 MEIGUI YUAN QU E 3 BAIYUGUANGZHOU GUANGDONG                                                                                                  Q067                                                                                                       CHINA                         AUSTRALIA                                                                                                                                                                                                      GU ;                                                """


class TestLoader(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._loader = nparcel.Loader()
        cls._job_ts = cls._loader.db.date_now()

    def test_init(self):
        """Initialise a Loader object.
        """
        msg = 'Object is not an nparcel.Loader'
        self.assertIsInstance(self._loader, nparcel.Loader, msg)

    def test_parser_integration(self):
        """Parser object integration.
        """
        msg = 'Loader object does not have a valid Parser object'
        self.assertIsInstance(self._loader.parser, nparcel.Parser, msg)

    def test_valid_barcode_extract(self):
        """Extract valid barcode.
        """
        result = self._loader.parser.parse_line(VALID_LINE)
        received = result.get('Bar code')
        expected = VALID_LINE_BARCODE
        msg = 'Loader Bar code parse should return "%s"' % expected
        self.assertEqual(received, expected, msg)

    def test_processor_valid_record(self):
        """Process valid raw T1250 line.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        msg = 'Valid T1250 record should process OK'
        self.assertTrue(self._loader.process(self._job_ts,
                                             VALID_LINE,
                                             FILE_BU.get('tolp')),
                        msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_processor_valid_record_single_quote(self):
        """Process valid raw T1250 line.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'V098'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        msg = 'Valid T1250 record should process OK -- single quote'
        self.assertTrue(self._loader.process(self._job_ts,
                                             SINGLE_QUOTE_LINE,
                                             FILE_BU.get('tolp')),
                        msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_processor_valid_record_dodgy_postcode(self):
        """Process valid raw T1250 line -- dodgy postcode.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'Q067'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        msg = 'Valid T1250 record should process OK -- bad postcode'
        self.assertTrue(self._loader.process(self._job_ts,
                                             DODGY_POSTCODE,
                                             FILE_BU.get('tolp')), msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_processor_valid_record_update(self):
        """Process valid raw T1250 line with a "job" item Agent Id update.
        """
        # Seed the Agent Ids.
        agent_fields = {'code': 'N031'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))
        agent_fields = {'code': 'N014'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        msg = 'Valid T1250 record should process successfully'
        self.assertTrue(self._loader.process(self._job_ts,
                                             VALID_LINE,
                                             FILE_BU.get('tolp')), msg)
        msg = 'Valid T1250 record update should process successfully'
        self.assertTrue(self._loader.process(self._job_ts,
                                             VALID_LINE_AGENT_UPD,
                                             FILE_BU.get('tolp')), msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_processor_invalid_postcode_record(self):
        """Process valid raw T1250 line -- missing Postcode.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        msg = 'T1250 record should process successfully -- missing postcode'
        self.assertTrue(self._loader.process(self._job_ts,
                                             INVALID_POSTCODE_LINE,
                                             FILE_BU.get('tolp')), msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_processor_missing_agent_id_record(self):
        """Process valid raw T1250 line -- missing Agent Id.
        """
        msg = 'Missing Agent Id should fail processing'
        self.assertFalse(self._loader.process(self._job_ts,
                                              VALID_LINE,
                                              FILE_BU.get('tolp')), msg)

    def test_processor_valid_record_existing_barcode(self):
        """Process valid raw T1250 line -- existing barcode.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        # First, create a record and attempt to reload as a duplicate.
        # Should update the Agent Id but not create a new job_item record.
        msg = 'New T1250 record should process successfully'
        self.assertTrue(self._loader.process(self._job_ts,
                                             VALID_LINE,
                                             FILE_BU.get('tolp')), msg)
        msg = 'Duplicate T1250 record should process successfully'
        self.assertTrue(self._loader.process(self._job_ts,
                                             VALID_LINE,
                                             FILE_BU.get('tolp')), msg)

        sql = self._loader.db.jobitem.connote_sql(VALID_LINE_CONNOTE)
        self._loader.db(sql)
        received = []
        for row in self._loader.db.rows():
            received.append(row[0])
        expected = 1
        msg = 'Connote update should not create additional job_item'
        self.assertEqual(len(received), expected, msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_processor_invalid_barcode_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        msg = 'Invalid barcode processing should return False'
        self.assertFalse(self._loader.process(self._job_ts,
                                              INVALID_BARCODE_LINE,
                                              FILE_BU.get('tolp')), msg)

    def test_processor_invalid_agent_id_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        msg = 'Invalid Agent Id processing should return False'
        self.assertFalse(self._loader.process(self._job_ts,
                                              INVALID_AGENTID_LINE,
                                              FILE_BU.get('tolp')), msg)

    def test_processor_manufactured_connote(self):
        """Process valid raw T1250 line with manufactured barcode.
        """
        # Seed the Agent Id.
        agent_fields = [{'code': 'N031'},
                        {'code': 'N032'}]
        for agent_field in agent_fields:
            self._loader.db(self._loader.db._agent.insert_sql(agent_field))

        # First, create a manufactured barcode value.
        msg = 'Manufactured barcode creation failed -- no barcode'
        self.assertTrue(self._loader.process(self._job_ts,
                                             MANUFACTURED_BC_LINE,
                                             FILE_BU.get('tolp')), msg)
        # Now the manufactured barcode value update.
        msg = 'Manufactured barcode creation failed -- existing barcode'
        self.assertTrue(self._loader.process(self._job_ts,
                                             MANUFACTURED_BC_UPD_LINE,
                                             FILE_BU.get('tolp')), msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_table_column_map(self):
        """Map parser fields to table columns.
        """
        fields = {'Field 1': 'field 1 value',
                  'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'column': 'field_2',
                   'required': True}}
        received = self._loader.table_column_map(fields, map)
        expected = {'field_1': 'field 1 value',
                    'field_2': 'field 2 value'}
        msg = 'Table to column map incorrect'
        self.assertDictEqual(received, expected, msg)

    def test_table_column_map_missing_required_field_exception(self):
        """Table column map missing required field exception -- no default.
        """
        fields = {'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'value': 'field_2',
                   'required': False}}
        self.assertRaisesRegexp(ValueError,
                                'Field "Field 1" is required',
                                self._loader.table_column_map,
                                fields, map)

    def test_table_column_map_missing_required_field_with_default(self):
        """Table column map missing required field value with default.
        """
        fields = {'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True,
                   'default': 'field_1_default'},
               'Field 2': {
                   'column': 'field_2',
                   'required': False}}
        received = self._loader.table_column_map(fields, map)
        expected = {'field_1': 'field_1_default',
                    'field_2': 'field 2 value'}
        msg = 'Table to column map with missing required field error'
        self.assertDictEqual(received, expected, msg)

    def test_table_column_map_missing_required_field_with_default_eq(self):
        """Table column map missing required field value with default_equal.
        """
        fields = {'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True,
                   'default_equal': 'Field 2'},
               'Field 2': {
                   'column': 'field_2',
                   'required': False}}
        received = self._loader.table_column_map(fields, map)
        expected = {'field_1': 'field 2 value',
                    'field_2': 'field 2 value'}
        msg = 'Table to column map with missing required field error'
        self.assertDictEqual(received, expected, msg)

    def test_table_column_map_for_a_valid_raw_record(self):
        """Process valid raw T1250 line and map job table elements.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        fields = self._loader.parser.parse_line(VALID_LINE)
        fields['job_ts'] = self._job_ts
        fields['bu_id'] = int(FILE_BU.get('tolp'))
        received = self._loader.table_column_map(fields,
                                                 nparcel.loader.JOB_MAP)
        expected = {'address_1': '31 Bridge st,',
                    'address_2': 'Lane Cove,',
                    'agent_id': 1,
                    'bu_id': 1,
                    'card_ref_nbr': '4156536111',
                    'job_ts': self._job_ts,
                    'postcode': '2066',
                    'state': 'NSW',
                    'status': 1,
                    'suburb': 'Australia Other'}
        msg = 'Valid record Job table translation error'
        self.assertDictEqual(received, expected, msg)

    def test_valid_translate_postcode_non_integer(self):
        """Translate postcode to state -- valid, range-based.
        """
        postcode = 'xxx'
        received = self._loader.translate_postcode(postcode)
        expected = ''
        msg = 'Non-integer postcode translation to state failed'
        self.assertEqual(received, expected, msg)

    def test_valid_translate_postcode_range_based(self):
        """Translate postcode to state -- valid, range-based.
        """
        postcode = 2000
        received = self._loader.translate_postcode(postcode)
        expected = 'NSW'
        msg = 'Valid postcode translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

    def test_invalid_translate_postcode_range_based(self):
        """Translate postcode to state -- invalid, range-based.
        """
        postcode = -1
        received = self._loader.translate_postcode(postcode)
        expected = ''
        msg = 'Invalid postcode translation to state failed -- invalid'
        self.assertEqual(received, expected, msg)

    def test_valid_translate_postcode_exception_based(self):
        """Translate postcode to state -- valid, exception-based.
        """
        postcode = 2899
        received = self._loader.translate_postcode(postcode)
        expected = 'NSW'
        msg = 'Valid postcode translation to state failed -- exceptions'
        self.assertEqual(received, expected, msg)

    def test_jobitem_table_column_map_for_a_valid_raw_record(self):
        """Process valid raw T1250 line and map "jobitem" table elements.
        """
        fields = self._loader.parser.parse_line(VALID_LINE)
        received = self._loader.table_column_map(fields,
                                                 nparcel.loader.JOB_ITEM_MAP)
        # Null out the time created.
        received['created_ts'] = None
        expected = {'connote_nbr': '218501217863',
                    'item_nbr': '218501217863',
                    'consumer_name': 'Diane Donohoe',
                    'pieces': '00001',
                    'status': 1,
                    'created_ts': None}
        msg = 'Valid record "jobitem" table translation error'
        self.assertDictEqual(received, expected, msg)

    def test_barcode_exists_with_missing_barcode(self):
        """Check barcode status -- missing barcode.
        """
        msg = 'Missing barcode should return False'
        self.assertFalse(self._loader.barcode_exists('xxx'), msg)

    def test_barcode_exists_with_existing_barcode(self):
        """Check barcode status -- existing barcode.
        """
        # Seed the barcode.
        barcode_fields = {'card_ref_nbr': VALID_LINE_BARCODE,
                          'job_ts': self._job_ts}
        self._loader.db(self._loader.db._job.insert_sql(barcode_fields))

        msg = 'Existing barcode should return True'
        self.assertTrue(self._loader.barcode_exists(VALID_LINE_BARCODE),
                        msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_agent_id_with_missing_agent_id(self):
        """Agent ID check with missing Agent ID.
        """
        msg = 'Missing Agent ID should return None'
        self.assertIsNone(self._loader.get_agent_id('xxx'), msg)

    def test_agent_id_existing_agent_id(self):
        """Valid agent ID check.
        """
        # Seed the Agent Id.
        test_agent_id = 'N014'
        agent_fields = {'code': test_agent_id}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        msg = 'Existing barcode should not return None'
        received = self._loader.get_agent_id(test_agent_id)
        expected = 1
        self.assertEqual(received, expected, msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_match_connote_scenario_connote_lt_15_char(self):
        """Manufactured connote check -- connote < 15 chars.
        """
        msg = 'Connote length < 15 chars scenario check should return False'
        barcode = '41566627'
        connote = '218701663454'
        received = self._loader.match_connote(connote, barcode)
        self.assertFalse(received, msg)

    def test_match_connote_scenario_connote_gt_15_char_unique_barcode(self):
        """Manufactured connote check -- unique barcode, connote > 15 chars.
        """
        msg = 'Connote length > 15 chars scenario check should return False'
        barcode = '41566627'
        connote = '3142357006912345'
        received = self._loader.match_connote(connote, barcode)
        self.assertFalse(received, msg)

    def test_match_connote_scenario_connote_gt_15_char_dodgy_barcode(self):
        """Manufactured connote check -- dodgy barcode, connote > 15 chars.
        """
        msg = 'Connote length > 15 chars scenario check should return False'
        barcode = '000931423570069'
        connote = '3142357006912345'
        received = self._loader.match_connote(connote, barcode)
        self.assertTrue(received, msg)

    def test_match_connote_scenario_connote_gt_15_char_like_start(self):
        """Manufactured connote check -- like start, connote > 15 chars.
        """
        msg = 'Connote length > 15 chars scenario check should return False'
        barcode = '000931423750069'
        connote = '00093142375006909983'
        received = self._loader.match_connote(connote, barcode)
        self.assertTrue(received, msg)

    def test_get_connote_job_id(self):
        """Get connote-based job id.
        """
        older_ts = datetime.datetime.now() - datetime.timedelta(seconds=999)
        kwargs = {'address_1': '31 Bridge st,',
                  'address_2': 'Lane Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536111',
                  'job_ts': '%s' % older_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        sql = self._loader.db.job.insert_sql(kwargs)
        job_id_old = self._loader.db.insert(sql)

        kwargs = {'address_1': '31 Bridge st,',
                  'address_2': 'Lane Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536111',
                  'job_ts': self._job_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        sql = self._loader.db.job.insert_sql(kwargs)
        job_id = self._loader.db.insert(sql)

        kwargs = {'address_1': '32 Banana st,',
                  'address_2': 'Banana Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536112',
                  'job_ts': self._job_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        sql = self._loader.db.job.insert_sql(kwargs)
        dodgy_job_id = self._loader.db.insert(sql)

        # "job_items" table.
        jobitems = [{'connote_nbr': '218501217863',
                     'job_id': job_id,
                     'pickup_ts': self._job_ts,
                     'pod_name': 'pod_name 218501217863'},
                    {'connote_nbr': '218501217863',
                     'job_id': job_id_old,
                     'pickup_ts': self._job_ts,
                     'pod_name': 'pod_name 218501217863'},
                    {'connote_nbr': '111111111111',
                     'job_id': dodgy_job_id,
                     'pickup_ts': self._job_ts,
                     'pod_name': 'pod_name 111111111111'}]
        for jobitem in jobitems:
            sql = self._loader.db.jobitem.insert_sql(jobitem)
            self._loader.db(sql=sql)

        received = self._loader.get_connote_job_id(connote='218501217863')
        msg = 'Connote based job id query results not as expected'
        self.assertEqual(received, job_id, msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_email_no_agent_id(self):
        """Email attempt with no agent_id.
        """
        recipients = ['dummy@dummyville.com']
        agent_id = 1
        barcode = 'xxx'
        received = self._loader.send_email(agent_id,
                                           recipients,
                                           barcode,
                                           dry=True)
        msg = 'Email with no Agent Id should return False'
        self.assertFalse(received, msg)

    def test_email_agent_id(self):
        """Email attempt with agent_id.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031',
                        'name': 'Auburn Newsagency',
                        'address': '119 Auburn Road',
                        'suburb': 'HAWTHORN EAST',
                        'postcode': '3123'}
        sql = self._loader.db._agent.insert_sql(agent_fields)
        id = self._loader.db.insert(sql)

        recipients = ['dummy@dummyville.com']
        agent_id = id
        barcode = 'xxx'
        received = self._loader.send_email(agent_id,
                                           recipients,
                                           barcode,
                                           dry=True)
        msg = 'Email with valid Agent Id should return True'
        self.assertTrue(received, msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_sms_no_agent_id(self):
        """SMS attempt with no agent_id.
        """
        recipients = ['1234567890']
        agent_id = 1
        barcode = 'xxx'
        received = self._loader.send_sms(agent_id,
                                         recipients,
                                         barcode,
                                         dry=True)
        msg = 'SMS with no Agent Id should return False'
        self.assertFalse(received, msg)

    def test_sms_agent_id(self):
        """SMS attempt with agent_id.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031',
                        'name': 'Auburn Newsagency',
                        'address': '119 Auburn Road',
                        'suburb': 'HAWTHORN EAST',
                        'postcode': '3123'}
        sql = self._loader.db._agent.insert_sql(agent_fields)
        id = self._loader.db.insert(sql)

        recipients = ['0431602145']
        agent_id = id
        barcode = 'xxx'
        received = self._loader.send_sms(agent_id,
                                         recipients,
                                         barcode,
                                         dry=True)
        msg = 'SMS with valid Agent Id should return True'
        self.assertTrue(received, msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    @classmethod
    def tearDownClass(cls):
        cls._loader = None
        cls._job_ts = None
