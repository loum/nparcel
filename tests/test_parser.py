import unittest2

import nparcel


class TestParser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._p = nparcel.Parser()
        cls._field = {'dummy field': {'offset': 0,
                                      'length': 20}}
        cls._fields = {'Conn Note': {'offset': 0,
                                     'length': 20},
                       'Identifier': {'offset': 21,
                                      'length': 20},
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
                       'Bar code': {'offset': 438,
                                    'length': 15},
                       'Agent Id': {'offset': 453,
                                    'length': 4},
                       'Pieces': {'offset': 588,
                                  'length': 5}}
        cls._line = """006499335802          YMLML11TOLP130413  Hannah Sewell                           51 Westbourne St.             Stanmore                      Sydney                        2048                                                                                                                 Hannah Sewell                             RUSTIN AND MALLORY RETAIL LTD REDDITCH                                                                      4156778061     N014                                                                                                                                   00001000001                                                                      Parcels Overnight                   UNIT 27 DUNLOP ROAD           HUNT END INDUSTRIAL ESTATE                                                                                           N014                                                                                                       GB                            AUSTRALIA                                                                                                                                                                                                         Ne                                               """

    def test_init(self):
        """Initialise a Parser object.
        """
        p = nparcel.Parser()
        msg = 'Object is not an nparcel.Parser'
        self.assertIsInstance(p, nparcel.Parser, msg)

    def test_set_empty_field(self):
        """Set field with empty dictionary.
        """
        self._p.fields = {}
        received = self._p.fields
        expected = {}
        msg = 'Setting field with empty list should not produce error.'
        self.assertDictEqual(received, expected, msg)

    def test_set_non_dictionary_based_field(self):
        """Set field with non-dictionary value.
        """
        with self.assertRaises(TypeError) as cm:
            self._p.fields = ''

        exception = cm.exception
        received = str(exception)
        expected = 'Token assignment expected dictionary'
        msg = 'Setting field with non-dictionary should raise TypeError.'
        self.assertEqual(received, expected, msg)

    def test_init_valid_field(self):
        """Set field with valid dictionary value.
        """
        fields = {'Conn Note': {'offset': 0,
                                'length': 20}}
        parser = nparcel.Parser(fields=fields)
        received = parser.fields
        expected = fields
        msg = 'Fields initialisation property setter/getter error.'
        self.assertEqual(received, expected, msg)

    def test_parse_no_fields(self):
        """Line parse with no fields should return None.
        """
        received = self._p.parse_line(self._line)
        expected = {}
        msg = 'Line parse with no fields should return None'
        self.assertDictEqual(received, expected, msg)

    def test_parse_conn_note_field(self):
        """Line parse with Conn Note field.
        """
        fields = {'Conn Note': {'offset': 0,
                                'length': 20}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Conn Note': '006499335802'}
        msg = 'Conn Note field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_identifier_field(self):
        """Line parse with Identifier field.
        """
        fields = {'Identifier': {'offset': 21,
                                 'length': 20}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Identifier': ' YMLML11TOLP130413'}
        msg = 'Identifier field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_consumer_name_field(self):
        """Line parse with Consumer Name field.
        """
        fields = {'Consumer Name': {'offset': 41,
                                    'length': 30}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Consumer Name': 'Hannah Sewell'}
        msg = 'Consumer Name field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_consumer_address_1_field(self):
        """Line parse with Consumer Address 1 field.
        """
        fields = {'Consumer Address 1': {'offset': 81,
                                         'length': 30}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Consumer Address 1': '51 Westbourne St.'}
        msg = 'Consumer Address 1 field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_consumer_address_2_field(self):
        """Line parse with Consumer Address 2 field.
        """
        fields = {'Consumer Address 2': {'offset': 111,
                                         'length': 30}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Consumer Address 2': 'Stanmore'}
        msg = 'Consumer Address 2 field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_suburb_field(self):
        """Line parse with Suburb field.
        """
        fields = {'Suburb': {'offset': 141,
                             'length': 30}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Suburb': 'Sydney'}
        msg = 'Suburb field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_post_code_field(self):
        """Line parse with Post code field.
        """
        fields = {'Post code': {'offset': 171,
                                'length': 4}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Post code': '2048'}
        msg = 'Post code field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_bar_code_field(self):
        """Line parse with Bar code field.
        """
        fields = {'Bar code': {'offset': 438,
                               'length': 15}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Bar code': '4156778061'}
        msg = 'Bar code field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_agent_id_field(self):
        """Line parse with Agent Id field.
        """
        fields = {'Agent Id': {'offset': 453,
                               'length': 4}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Agent Id': 'N014'}
        msg = 'Agent Id field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_pieces_field(self):
        """Line parse with Pieces field.
        """
        fields = {'Pieces': {'offset': 588,
                             'length': 5}}
        p = nparcel.Parser(fields=fields)
        received = p.parse_line(self._line)
        expected = {'Pieces': '00001'}
        msg = 'Pieces field parse incorrect'
        self.assertEqual(received, expected, msg)

    def test_parse_all(self):
        """Line parse with all fields.
        """
        p = nparcel.Parser(fields=self._fields)
        received = p.parse_line(self._line)
        expected = {'Conn Note': '006499335802',
                    'Identifier': ' YMLML11TOLP130413',
                    'Consumer Name': 'Hannah Sewell',
                    'Consumer Address 1': '51 Westbourne St.',
                    'Consumer Address 2': 'Stanmore',
                    'Suburb': 'Sydney',
                    'Post code': '2048',
                    'Bar code': '4156778061',
                    'Agent Id': 'N014',
                    'Pieces': '00001'}
        msg = 'All field parse incorrect'
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._p = None
        cls._line = None
        cls._fields = None
