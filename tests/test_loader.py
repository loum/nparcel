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
        msg = 'T1250 record with invalid barcode should fail processing'
        self.assertFalse(self._loader.process(INVALID_BARCODE_LINE), msg)

    def test_processor_invalid_agent_id_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        msg = 'T1250 record with invalid Agent Id should fail processing'
        self.assertFalse(self._loader.process(INVALID_AGENTID_LINE), msg)

    def test_table_column_map(self):
        """Map parser fields to table columns.
        """
        fields = {'Field 1': 'field 1 value',
                  'Field 2': 'field 2 value'}
        map = {'Field 1': 'field_1',
               'Field 2': 'field_2'}
        received = self._loader.table_column_map(fields, map)
        expected = {'field_1': 'field 1 value',
                    'field_2': 'field 2 value'}
        msg = 'Table to column map incorrect'
        self.assertDictEqual(received, expected, msg)

    def test_table_column_map_extra_fields(self):
        """Map extra parser fields to table columns.
        """
        fields = {'Field 1': 'field 1 value',
                  'Field 2': 'field 2 value'}
        map = {'Field 1': 'field_1'}
        self.assertRaisesRegexp(ValueError,
                                'Cannot map fields "Field 2',
                                self._loader.table_column_map,
                                fields, map)

    @classmethod
    def tearDownClass(cls):
        cls._loader = None
