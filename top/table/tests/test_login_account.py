import unittest2
import os

import top


class TestLoginAccount(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._la = top.LoginAccount()
        cls._db = top.DbSession()
        cls._db.connect()

    def test_init(self):
        """Placeholder test to make sure the LoginAccount table is
        created.
        """
        msg = 'Object is not an top.LoginAccount'
        self.assertIsInstance(self._la, top.LoginAccount, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._la = None
