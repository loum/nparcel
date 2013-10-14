import unittest2

import nparcel


class TestPrimaryElectDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf_file = 'nparcel/conf/nparceld.conf'
        cls._d = nparcel.PrimaryElectDaemon(pidfile=None, config=conf_file)
        cls._test_file = 'nparcel/tests/stop_report_short.csv'

    def test_init(self):
        """Intialise a PrimaryElectDaemon object.
        """
        msg = 'Not a nparcel.PrimaryElectDaemon object'
        self.assertIsInstance(self._d, nparcel.PrimaryElectDaemon, msg)

    def test_start(self):
        """Primary Elect _start processing loop.
        """
        self._d.set_dry()
        self._d.set_file(self._test_file)
        self._d._start(self._d.exit_event)

    @classmethod
    def tearDownClass(cls):
        cls._d = None
        cls._test_file = None
        del cls._test_file
