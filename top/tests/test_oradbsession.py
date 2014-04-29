import unittest2
import os

import nparcel

DUMMY_SCHEMA = ['id INTEGER PRIMARY KEY',
                'dummy_field CHAR(15)']


class TestOraDbSession(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._db = nparcel.OraDbSession()
        cls._db.connect()
        cls._db.create_table(name='dummy', schema=DUMMY_SCHEMA)
        cls._db.create_table(name='v_nparcel_adp_connotes',
                             schema=cls._db.transsend.schema)

    def test_insert(self):
        """Insert into the DB table.
        """
        sql = """INSERT INTO dummy (dummy_field)
VALUES ('xxx')"""
        received = self._db.insert(sql)
        expected = 1
        msg = 'Insert should return the row ID'
        self.assertEqual(received, expected, msg)

        # and clean up.
        self._db.connection.rollback()

    def test_columns(self):
        """Verify table column names.
        """
        sql = """SELECT * FROM dummy"""
        self._db(sql)
        received = self._db.columns()
        expected = ['id', 'dummy_field']
        msg = 'Dummy table column names not as expected'
        self.assertListEqual(received, expected, msg)

    def test_initialisation_to_real_oracle_db(self):
        """Placeholder for real DB connectivity (disabled by default).
        """
        # To enable real DB connectivity, update the connection string
        # and set the disabled to False.
        disabled = True

        kwargs = {'host': 'host',
                  'user': 'user',
                  'password': 'password',
                  'port': 1521,
                  'sid': 'sid'}
        db = nparcel.OraDbSession(kwargs)

        # Check the connection string.
        # Tweak the password to suit.
        received = db.conn_string
        expected = 'user/password@host:1521/sid'
        msg = 'Oracle DB connection string error'
        self.assertEqual(received, expected, msg)

        if not disabled:
            db.connect()
            db.disconnect()

    def test_load_fixture(self):
        """Load a fixture into a table -- dodgy table name.
        """
        fixture_file = os.path.join('nparcel',
                                    'tests',
                                    'fixtures',
                                    'transsend.py')
        received = self._db.load_fixture(self._db.transsend, fixture_file)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
