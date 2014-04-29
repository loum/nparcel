import unittest2
import os

import top


class TestParcelSize(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._p_size = top.ParcelSize()
        cls._db = top.DbSession()
        cls._db.connect()

        db = cls._db
        fixture_dir = os.path.join('top', 'tests', 'fixtures')
        fixtures = [{'db': db.parcel_size, 'fixture': 'parcel_sizes.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Placeholder test to make sure the ParcelSize table is created.
        """
        msg = 'Object is not an top.ParcelSize'
        self.assertIsInstance(self._p_size, top.ParcelSize, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._p_size = None
