import unittest2

import nparcel


class TestExporterDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._ed = nparcel.ExporterDaemon(pidfile=None,
                                         config='nparcel/conf/nparceld.conf')

    def test_init(self):
        """Intialise a ExporterDaemon object.
        """
        msg = 'Not a nparcel.ExporterDaemon object'
        self.assertIsInstance(self._ed, nparcel.ExporterDaemon, msg)

    def test_start(self):
        self._ed._start(self._ed.exit_event)

    @classmethod
    def tearDownClass(cls):
        cls._ed = None
