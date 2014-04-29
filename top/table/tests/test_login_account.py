import unittest2
import os

import nparcel


class TestLoginAccount(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._la = nparcel.LoginAccount()
        cls._db = nparcel.DbSession()
        cls._db.connect()

    def test_init(self):
        """Placeholder test to make sure the LoginAccount table is
        created.
        """
        msg = 'Object is not an nparcel.LoginAccount'
        self.assertIsInstance(self._la, nparcel.LoginAccount, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._la = None
