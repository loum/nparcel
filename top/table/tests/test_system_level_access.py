import unittest2
import os

import top


class TestSystemLevelAccess(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._sla = top.SystemLevelAccess()
        cls._db = top.DbSession()
        cls._db.connect()

        fixture_dir = os.path.join('top', 'tests', 'fixtures')
 
        db = cls._db
        fixtures = [{'db': db.system_level_access,
                     'fixture': 'system_level_accesses.py'}]

        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Placeholder test to make sure the SystemLevelAccess table is
        created.
        """
        msg = 'Object is not an top.SystemLevelAccess'
        self.assertIsInstance(self._sla, top.SystemLevelAccess, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._sla = None
