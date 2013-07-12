import unittest2

import nparcel


class TestLoader(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._valid_line = """218501217863          YMLML11TOLP130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """

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
        result = l.parser.parse_line(self._valid_line)
        received = result.get('Bar code')
        expected = '4156536111'
        msg = 'Loader Bar code parse should return "%s"' % expected
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._valid_line = None
