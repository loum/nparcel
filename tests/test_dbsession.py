import unittest2
import os

import nparcel


class TestDbSession(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._db = nparcel.DbSession()
        cls._db.connect()

    def test_init(self):
        """
        """
        pass

    @classmethod
    def tearDownClass(cls):
        cls._db = None
        os.remove('test.db')
