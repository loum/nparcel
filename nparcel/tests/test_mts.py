import unittest2

import nparcel


class TestMts(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._mts = nparcel.Mts(config='nparcel/conf/npmts.conf')

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

    @classmethod
    def tearUpClass(cls):
        cls._mts = None
        del cls._mts
