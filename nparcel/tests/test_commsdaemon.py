import unittest2
import tempfile

import nparcel


class TestCommsDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf_file = 'nparcel/conf/nparceld.conf'
        cls._cd = nparcel.CommsDaemon(pidfile=None, config=conf_file)

    def test_init(self):
        """Initialise a CommsDaemon object.
        """
        msg = 'Not a nparcel.CommsDaemon object'
        self.assertIsInstance(self._cd, nparcel.CommsDaemon, msg)

    def test_start(self):
        """Start file processing loop.
        """
        self._cd.dry = True
        self._cd._start(self._cd.exit_event)

    @classmethod
    def tearDownClass(cls):
        cls._cd = None
        del cls._cd
