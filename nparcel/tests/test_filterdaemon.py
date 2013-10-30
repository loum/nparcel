import unittest2

import nparcel


class TestFilterDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._fd = nparcel.FilterDaemon(pidfile=None,
                                       config='nparcel/conf/nparceld.conf')

    def test_init(self):
        """Initialise a FilterDaemon object.
        """
        msg = 'Not a nparcel.FilterDaemon object'
        self.assertIsInstance(self._fd, nparcel.FilterDaemon, msg)

    @classmethod
    def tearDownClass(cls):
        cls._fd = None
        del cls._fd
