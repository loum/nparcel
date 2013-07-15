import unittest2

import nparcel

VALID_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
INVALID_BARCODE_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                                              N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """

INVALID_AGENTID_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111                                                                                                                                            00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """


class TestLoader(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._loader = nparcel.Loader()

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
        expected = '4156536111'
        msg = 'Loader Bar code parse should return "%s"' % expected
        self.assertEqual(received, expected, msg)

    def test_validation_missing_barcode(self):
        """Validate record with missing barcode.
        """
        result = {'Bar code': ''}
        self.assertRaisesRegexp(ValueError,
                                'Missing barcode',
                                self._loader.validate,
                                fields=result)

    def test_validation_valid_barcode(self):
        """Validate record with valid barcode.
        """
        result = {'Bar code': '4156536111',
                  'Agent Id': 'dummy'}
        msg = 'Loader validation with valid Bar code should return True'
        self.assertTrue(self._loader.validate(fields=result), msg)

    def test_validation_missing_agent_id(self):
        """Validate record with missing agent id.
        """
        result = {'Bar code': 'dummy',
                  'Agent Id': ''}
        self.assertRaisesRegexp(ValueError,
                                'Missing Agent Id',
                                self._loader.validate,
                                fields=result)

    def test_validation_valid_agent_id(self):
        """Validate record with valid barcode.
        """
        result = {'Bar code': 'dummy',
                  'Agent Id': 'N031'}
        msg = 'Loader validation with valid Agent Id should return True'
        self.assertTrue(self._loader.validate(fields=result), msg)

    def test_processor_valid_record(self):
        """Process valid raw T1250 line.
        """
        msg = 'Valid T1250 record should process successfully'
        self.assertTrue(self._loader.process(VALID_LINE), msg)

    def test_processor_invalid_barcode_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        self.assertRaisesRegexp(ValueError,
                                'Field "Bar code" is required',
                                self._loader.process,
                                INVALID_BARCODE_LINE)

    def test_processor_invalid_agent_id_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        self.assertRaisesRegexp(ValueError,
                                'Field "Agent Id" is required',
                                self._loader.process,
                                INVALID_AGENTID_LINE)

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
        fields = self._loader.parser.parse_line(VALID_LINE)
        received = self._loader.table_column_map(fields,
                                                 nparcel.loader.JOB_MAP)
        expected = {'address_1': '31 Bridge st,',
                    'address_2': 'Lane Cove,',
                    'agent_id': 'N031',
                    'bu_id': 1,
                    'card_ref_nbr': '4156536111',
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
        expected = None
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

    def test_job_item_table_column_map_for_a_valid_raw_record(self):
        """Process valid raw T1250 line and map job_item table elements.
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
        msg = 'Valid record "job_item" table translation error'
        self.assertDictEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._loader = None
