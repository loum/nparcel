import unittest2
import os

import top


class TestReturnsReference(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._rr = top.ReturnsReference()
        cls._db = top.DbSession()
        cls._db.connect()

        db = cls._db
        fixture_dir = os.path.join('top', 'tests', 'fixtures')
        fixtures = [{'db': db.returns_reference,
                     'fixture': 'returns_reference.py'},
                    {'db': db.returns, 'fixture': 'returns.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Placeholder test to make sure the ReturnsReference table is
        created.
        """
        msg = 'Object is not an top.ReturnsReference'
        self.assertIsInstance(self._rr, top.ReturnsReference, msg)

    def test_reference_nbr_sql(self):
        """Verify the reference_nbr_sql string.
        """
        returns_id = 2
        db_type = self._db.db_type

        sql = self._db.returns_reference.reference_nbr_sql(returns_id,
                                                           db=db_type)
        self._db(sql)

        received = list(self._db.rows())
        expected = [('bbbbbb',), ('cccccc',)]
        msg = 'reference_nbr_sql returned values error'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._rr = None
