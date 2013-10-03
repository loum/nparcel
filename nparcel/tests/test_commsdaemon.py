import unittest2

import nparcel


class TestCommsDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf_file = 'nparcel/conf/nparceld.conf'
        cls._comms = nparcel.CommsDaemon(pidfile=None, config=conf_file)

    def test_init(self):
        """Initialise a CommsDaemon object.
        """
        msg = 'Not a nparcel.CommsDaemon object'
        self.assertIsInstance(self._comms, nparcel.CommsDaemon, msg)

    @classmethod
    def tearDownClass(cls):
        cls._comms = None
        del cls._comms
