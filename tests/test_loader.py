import unittest2

import nparcel

VALID_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """

INVALID_BARCODE_LINE = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                                              N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
class TestLoader(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_init(self):
        """Initialise a Loader object.
        """
        l = nparcel.Loader()
        msg = 'Object is not an nparcel.Loader'
        self.assertIsInstance(l, nparcel.Loader, msg)

    def test_parser_integration(self):
        """Parser object integration.
        """
        l = nparcel.Loader()
        msg = 'Loader object does not have a valid Parser object'
        self.assertIsInstance(l.parser, nparcel.Parser, msg)

    def test_valid_barcode_extract(self):
        """Extract valid barvcode.
        """
        l = nparcel.Loader()
        result = l.parser.parse_line(VALID_LINE)
        received = result.get('Bar code')
        expected = '4156536111'
        msg = 'Loader Bar code parse should return "%s"' % expected
        self.assertEqual(received, expected, msg)

    def test_validation_missing_barcode(self):
        """Validate record with missing barcode.
        """
        l = nparcel.Loader()
        result = {'Bar code': ''}
        self.assertRaisesRegexp(ValueError,
                                'Missing barcode',
                                l.validate,
                                fields=result)

    def test_validation_valid_barcode(self):
        """Validate record with valid barcode.
        """
        l = nparcel.Loader()
        result = {'Bar code': '4156536111'}
        msg = 'Loader validation with valid Bar code should return True'
        self.assertTrue(l.validate(fields=result), msg)

    def test_processor_valid_record(self):
        """Process valid raw T1250 line.
        """
        l = nparcel.Loader()
        msg = 'Valid T1250 record should process successfully'
        self.assertTrue(l.process(VALID_LINE), msg)

    def test_processor_invalid_barcode_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        l = nparcel.Loader()
        msg = 'T1250 record with invalid barcode should fail processing'
        self.assertFalse(l.process(INVALID_BARCODE_LINE), msg)

    @classmethod
    def tearDownClass(cls):
        pass
