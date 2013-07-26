import unittest2
import os

import nparcel

DUMMY_SCHEMA = ['id INTEGER PRIMARY KEY',
                'dummy_field CHAR(15)']


class TestDbSession(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._db = nparcel.DbSession()
        cls._db.connect()
        cls._db.create_table(name='dummy', schema=DUMMY_SCHEMA)

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

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
