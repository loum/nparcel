import unittest2
import threading

import nparcel


class TestFilterDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/tests/files/T1250_TOLI_20130828202901.txt'
        cls._exit_event = threading.Event()
        cls._fd = nparcel.FilterDaemon(pidfile=None,
                                       config='nparcel/conf/nparceld.conf')

    def test_init(self):
        """Initialise a FilterDaemon object.
        """
        msg = 'Not a nparcel.FilterDaemon object'
        self.assertIsInstance(self._fd, nparcel.FilterDaemon, msg)

    def test_start(self):
        """Start dry loop.
        """
        # Note: were not testing behaviour here but check that we have
        # one of each, success/error/other.
        old_file = self._fd.file
        old_dry = self._fd.dry

        self._fd.set_dry()
        self._fd.set_file(self._file)
        self._fd._start(self._exit_event)

        # Clean up.
        self._fd.set_file(old_file)
        self._fd.set_dry(old_dry)
        self._exit_event.clear()

    @classmethod
    def tearDownClass(cls):
        del cls._file
        del cls._exit_event
        cls._fd = None
        del cls._fd
