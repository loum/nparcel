import unittest2
import os

import nparcel


class TestReturns(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._r = nparcel.Returns()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        db = cls._db
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.returns_reference,
                     'fixture': 'returns_reference.py'},
                    {'db': db.returns, 'fixture': 'returns.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Placeholder test to make sure the Returns table is
        created.
        """
        msg = 'Object is not an nparcel.Returns'
        self.assertIsInstance(self._r, nparcel.Returns, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._r = None
