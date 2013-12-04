import unittest2
import tempfile
import datetime
import os

import nparcel


class TestXlwriter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._x = nparcel.Xlwriter()

    def test_init(self):
        """Initialise a Xlwriter object.
        """
        msg = 'Object is not an nparcel.Xlwriter'
        self.assertIsInstance(self._x, nparcel.Xlwriter, msg)

    @classmethod
    def tearDownClass(cls):
        cls._x = None
        del cls._x
