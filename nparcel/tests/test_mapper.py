import unittest2

import nparcel


class TestMapper(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._m = nparcel.Mapper()

        test_conf = 'nparcel/tests/test_mapper.conf'
        cls._c = nparcel.Config(config_file=test_conf)

        cls.maxDiff = None

    def test_init(self):
        """Initialise a Mapper object.
        """
        msg = 'Object is not an nparcel.Mapper'
        self.assertIsInstance(self._m, nparcel.Mapper, msg)

    def test_parse_valid_line(self):
        """Parse the config.
        """
        line = self._c.get('test_lines', 'RAW01_PRIORITY_PE').strip('"')
        received = self._m.parser.parse_line(line)
        expected = {'ADP Type': 'PE',
                    'Agent Id or Location Id': 'N031',
                    'Bar code': '218501217863',
                    'Conn Note': '218501217863',
                    'Consumer Address 1': '31 Bridge st,',
                    'Consumer Address 2': 'Lane Cove,',
                    'Consumer Name': 'Lou Markovski',
                    'Email Address': 'loumar@tollgroup.com',
                    'Identifier': 'YMLML11TOLP130413',
                    'Item Number': '',
                    'Mobile Number': '0431602145',
                    'Pieces': '00001',
                    'Post code': '2066',
                    'Suburb': 'Australia Other',
                    'System Identifier': 'TOLP'}
        msg = 'Parsed line translation error'
        self.assertDictEqual(received, expected, msg)

    def test_translate(self):
        """Translate a valid, raw line.
        """
        line = self._c.get('test_lines', 'RAW01_PRIORITY_PE').strip('"')
        data_dict = self._m.parser.parse_line(line)
        received = self._m.translate(data_dict)
        expected = self._c.get('test_lines',
                               'RAW01_PRIORITY_PE_TRANSLATED').strip('"')
        msg = 'Translated line error'
        self.assertEqual(received, expected, msg)

    def test_process_valid_record(self):
        """Process valid record.
        """
        line = self._c.get('test_lines', 'RAW01_PRIORITY_PE').strip('"')
        received = self._m.process(line)
        expected = ('TOLP',
                    self._c.get('test_lines',
                                'RAW01_PRIORITY_PE_TRANSLATED').strip('"'))
        msg = 'Valid record processing error'
        self.assertTupleEqual(received, expected, msg)

    def test_process_non_pe_valid_record(self):
        """Process non-PE valid record.
        """
        line = self._c.get('test_lines', 'RAW01_PRIORITY_NO_PE').strip('"')
        received = self._m.process(line)
        expected = ()
        msg = 'Non-PE valid record processing error'
        self.assertTupleEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._m = None
        del cls._m
