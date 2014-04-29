import unittest2
import os

import nparcel


class TestLoginAccess(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._la = nparcel.LoginAccess()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')

        db = cls._db
        fixtures = [{'db': db.login_access, 'fixture': 'login_access.py'}]

        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Placeholder test to make sure the LoginAccess table is
        created.
        """
        msg = 'Object is not an nparcel.LoginAccess'
        self.assertIsInstance(self._la, nparcel.LoginAccess, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._la = None
