import unittest2

import nparcel


class TestMts(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._mts = nparcel.Mts(config='nparcel/conf/npmts.conf')
        cls._mts.set_template_dir('nparcel/templates')

    def test_init(self):
        """Initialise a MTS object.
        """
        msg = 'Object is not an nparcel.Mts'
        self.assertIsInstance(self._mts, nparcel.Mts, msg)

    def test_db_kwargs(self):
        """Verify the DB kwargs.
        """
        received = self._mts.db_kwargs()
        expected = {'host': 'host',
                    'user': 'user',
                    'password': 'password',
                    'port': 1521,
                    'sid': 'sid'}
        msg = 'Database kwargs error'
        self.assertDictEqual(received, expected, msg)

    def test_db_connection_string(self):
        """DB connection string.
        """
        received = self._mts.conn_string
        expected = 'user/password@host:1521/sid'
        msg = 'DB connection string error'
        self.assertEqual(received, expected, msg)

    def test_parse_config_items(self):
        """Verify required configuration items.
        """
        self._mts._parse_config()

        # Report range
        msg = 'Report range error'
        received = self._mts.report_range
        expected = 7
        self.assertEqual(received, expected, msg)

        # Display headers
        msg = 'Display headers error'
        received = self._mts.display_headers
        self.assertTrue(received, msg)

        # Output directory
        msg = 'Report output directry error'
        received = self._mts.out_dir
        expected = '/data/nparcel/mts'
        self.assertEqual(received, expected, msg)

    def test_report_no_db_connection(self):
        """Generate a delivery report with no DB connection.
        """
        dry = False
        received = self._mts.report(dry=dry)
        msg = 'Report run with no DB connection should return None'
        self.assertIsNone(received, msg)

    def test_report(self):
        """Generate a delivery report.
        """
        dry = True
        if not dry:
            self._mts.set_report_range(1)
            self._mts.connect()

        received = self._mts.report(dry=dry)

        if not dry:
            self._mts.disconnect()

        msg = 'Report run should return a non-None filename string'
        self.assertIsNotNone(received, msg)

    @classmethod
    def tearUpClass(cls):
        cls._mts = None
        del cls._mts
