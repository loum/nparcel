import unittest2

import top

SCHEMA = ["id INTEGER PRIMARY KEY",
          "sample_char CHAR(20)",
          "sample_int INT"]


class TestTable(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._table = top.Table(name='dummy')
        cls._db = top.DbSession()
        cls._db.connect()
        cls._db.create_table(name="dummy", schema=SCHEMA)

    def test_insert_valid_fields(self):
        """Insert valid fields into DB.
        """
        kwargs = {'sample_char': 'dummy',
                  'sample_int': 1}
        id = self._db.insert(self._table.insert_sql(kwargs))

        # Clean up.
        self._db.rollback()

    def test_update_valid_fields(self):
        """Insert valid fields into DB.
        """
        kwargs = {'sample_char': 'dummy',
                  'sample_int': 1}
        id = self._db.insert(self._table.insert_sql(kwargs))

        kwargs = {'sample_char': "can't",
                  'sample_int': 1}
        self._db(self._table.update_sql(kwargs))

        sql = """SELECT * FROM dummy WHERE id = %d""" % id
        self._db(sql)
        received = self._db.row
        expected = (1, "can't", 1)
        msg = 'Update error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._db.rollback()

    def test_update_valid_fields_where_clause(self):
        """Insert valid fields into DB with WHERE clause.
        """
        kwargs = {'sample_char': 'dummy',
                  'sample_int': 1}
        id_1 = self._db.insert(self._table.insert_sql(kwargs))

        kwargs = {'sample_char': 'funny',
                  'sample_int': 10}
        id_2 = self._db.insert(self._table.insert_sql(kwargs))

        kwargs = {'sample_char': "can't"}
        self._db(self._table.update_sql(kwargs, keys=(id_1, id_2)))

        sql = """SELECT * FROM dummy"""
        self._db(sql)
        received = list(self._db.rows())
        expected = [(1, "can't", 1), (2, "can't", 10)]
        msg = 'Update with WHERE clause error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        kwargs = {'sample_char': "funny"}
        self._db(self._table.update_sql(kwargs, keys=(id_2, )))

        sql = """SELECT * FROM dummy"""
        self._db(sql)
        received = list(self._db.rows())
        expected = [(1, "can't", 1), (2, "funny", 10)]
        msg = 'Update with WHERE clause error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._db.rollback()

    def test_update_sql(self):
        """Check UPDATE SQL statement.
        """
        kwargs = {'sample_char': 'xxx',
                  'sample_int': 1}
        received = self._table.update_sql(kwargs)
        expected = """UPDATE dummy
SET sample_int=1, sample_char='xxx'
"""
        msg = 'UPDATE SQL error'
        self.assertEqual(received, expected, msg)

    def test_update_sql_with_where_clause(self):
        """Check UPDATE SQL statement -- with where clause.
        """
        kwargs = {'sample_char': 'xxx',
                  'sample_int': 1}
        received = self._table.update_sql(kwargs, keys=(1,))
        expected = """UPDATE dummy
SET sample_int=1, sample_char='xxx'
WHERE id IN (1)"""
        msg = 'UPDATE SQL error with WHERE clause'
        self.assertEqual(received, expected, msg)

    def test_update_sql_with_where_clause_multiple_keys(self):
        """Check UPDATE SQL statement -- with where clause multiple keys.
        """
        kwargs = {'sample_char': 'xxx',
                  'sample_int': 1}
        received = self._table.update_sql(kwargs, keys=(1, 2))
        expected = """UPDATE dummy
SET sample_int=1, sample_char='xxx'
WHERE id IN (1, 2)"""
        msg = 'UPDATE SQL error with multiple keys'
        self.assertEqual(received, expected, msg)

    def test_sanitise(self):
        """Sanitise data kwargs for safe use in SQL DML.
        """
        values = [1, 'dummy']
        received = self._table.sanitise(values)
        expected = "1, 'dummy'"
        msg = 'SQL DML sanitise error - clear data'
        self.assertEqual(received, expected, msg)

        values = [10, "can't"]
        received = self._table.sanitise(values)
        expected = "10, 'can''t'"
        msg = 'SQL DML sanitise error - escape apostrophe'
        self.assertEqual(received, expected, msg)

    def test_sanitise_null_value(self):
        """Sanitise data kwargs for safe use in SQL DML - NULL values.
        """
        values = [1, 'NULL']
        received = self._table.sanitise(values)
        expected = "1, NULL"
        msg = 'SQL DML sanitise error - NULL values'
        self.assertEqual(received, expected, msg)

    def test_sanitise_return_list(self):
        """Sanitise data kwargs for safe use in SQL DML - return kwargs.
        """
        values = [1, "can't"]
        received = self._table.sanitise(values, as_string=False)
        expected = [1, "'can''t'"]
        msg = 'SQL DML sanitise error - return list with single quote'
        self.assertListEqual(received, expected, msg)

        values = [1, 'NULL']
        received = self._table.sanitise(values, as_string=False)
        expected = values
        msg = 'SQL DML sanitise error - return list with NULL value'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
