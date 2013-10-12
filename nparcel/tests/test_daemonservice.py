import unittest2

import nparcel


class TestDaemonService(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._ds = nparcel.DaemonService(pidfile=None)

    def test_init(self):
        """Intialise a DaemonService object.
        """
        msg = 'Not a nparcel.DaemonService object'
        self.assertIsInstance(self._ds, nparcel.DaemonService, msg)

    @classmethod
    def tearDownClass(cls):
        cls._ds = None
        del cls._ds
