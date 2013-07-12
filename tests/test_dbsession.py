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

    def test_create_table(self):
        """Dummy placeholder to ensure that the DB is created.
        """
        self._db.create_table(name='dummy',
                              schema=DUMMY_SCHEMA)

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
