import unittest2

import nparcel
import sqlite

SCHEMA = ["id INTEGER PRIMARY KEY",
          "sample_char CHAR(20)",
          "sample_int INT"]


class TestTable(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._table = nparcel.Table(name='dummy')
        cls._db = nparcel.DbSession()
        cls._db.connect()
        cls._db.create_table(name="dummy", schema=SCHEMA)

    def test_insert_unknown_field(self):
        """Insert an unknown column.
        """
        kwargs = {'dummy': 'dummy value'}
        self.assertRaisesRegexp(sqlite.DatabaseError,
                                'table dummy has no column named dummy',
                                self._db,
                                self._table.insert(kwargs))

    def test_insert_valid_fields(self):
        """Insert valid fields into DB.
        """
        kwargs = {'sample_char': 'dummy',
                  'sample_int': 1}
        id = self._db.insert(self._table.insert(kwargs))

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
