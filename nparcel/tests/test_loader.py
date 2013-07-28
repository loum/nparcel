import unittest2

import nparcel


VALID_LINE_BARCODE = '4156536111'
VALID_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
VALID_LINE_AGENT_UPD = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N014                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N014                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
INVALID_BARCODE_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                                              N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
INVALID_AGENTID_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111                                                                                                                                            00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
INVALID_POSTCODE_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other                                                                                                                                    Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """


class TestLoader(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._loader = nparcel.Loader()
        cls._job_ts = cls._loader.date_now()

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
        """Extract valid barvcode.
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

        msg = 'Valid T1250 record should process successfully'
        self.assertTrue(self._loader.process(self._job_ts, VALID_LINE), msg)

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
        self.assertTrue(self._loader.process(self._job_ts, VALID_LINE), msg)
        msg = 'Valid T1250 record update should process successfully'
        self.assertTrue(self._loader.process(self._job_ts,
                                             VALID_LINE_AGENT_UPD), msg)

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
                                             INVALID_POSTCODE_LINE), msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_processor_missing_agent_id_record(self):
        """Process valid raw T1250 line -- missing Agent Id.
        """
        msg = 'Missing Agent Id should fail processing'
        self.assertFalse(self._loader.process(self._job_ts,
                                              VALID_LINE), msg)

    def test_processor_valid_record_existing_barcode(self):
        """Process valid raw T1250 line -- existing barcode.
        """
        # Seed the barcode.
        barcode_fields = {'card_ref_nbr': VALID_LINE_BARCODE,
                          'job_ts': self._job_ts}
        self._loader.db(self._loader.db._job.insert_sql(barcode_fields))

        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        msg = 'T1250 record should process successfully -- existing barcode'
        self.assertTrue(self._loader.process(self._job_ts, VALID_LINE), msg)

        # Restore DB state.
        self._loader.db.connection.rollback()

    def test_processor_invalid_barcode_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        msg = 'Invalid barcode processing should return False'
        self.assertFalse(self._loader.process(self._job_ts,
                                              INVALID_BARCODE_LINE), msg)

    def test_processor_invalid_agent_id_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        msg = 'Invalid Agent Id processing should return False'
        self.assertFalse(self._loader.process(self._job_ts,
                                              INVALID_AGENTID_LINE), msg)

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

    def test_table_column_map_for_a_valid_raw_record(self):
        """Process valid raw T1250 line and map job table elements.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._loader.db(self._loader.db._agent.insert_sql(agent_fields))

        fields = self._loader.parser.parse_line(VALID_LINE)
        fields['job_ts'] = self._job_ts
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

    def test_valid_bu_id(self):
        """Convert identifier to business unit code.
        """
        bu_id = ' YMLML11TOLP130413'
        received = self._loader.translate_bu_id(bu_id)
        expected = 1
        msg = 'BU translation error -- valid BU'
        self.assertEqual(received, expected, msg)

    def test_invalid_bu_id(self):
        """Convert identifier to business unit code -- invalid.
        """
        bu_id = ' YMLML11TOLZ130413'
        received = self._loader.translate_bu_id(bu_id)
        expected = None
        msg = 'BU translation error -- invalid BU'
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

    @classmethod
    def tearDownClass(cls):
        cls._loader = None
        cls._job_ts = None
