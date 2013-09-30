import unittest2
import tempfile
import os

import nparcel


class TestService(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._comms_dir = tempfile.mkdtemp()
        cls._s = nparcel.Service(comms_dir=cls._comms_dir)

    def test_init(self):
        """Initialise a Service object.
        """
        msg = 'Object is not a nparcel.Service'
        self.assertIsInstance(self._s, nparcel.Service, msg)

    @classmethod
    def tearDownClass(cls):
        cls._s = None
        del cls._s
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
