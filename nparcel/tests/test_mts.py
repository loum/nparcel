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

    def test_mts_sql_query_template(self):
        """MTS query template.
        """
        received = self._mts.get_sql(template='mts_sql.t',
                                     base_dir='nparcel')
        expected = 'SELECT ds.'
        msg = 'MTS query error'
        self.assertEqual(received[:10], expected, msg)

    @classmethod
    def tearUpClass(cls):
        cls._mts = None
        del cls._mts
