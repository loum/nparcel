import unittest2

import nparcel


class TestExporterDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_init(self):
        """Intialise a ExporterDaemon object.
        """
        d = nparcel.ExporterDaemon(pidfile=None)
        msg = 'Not a nparcel.ExporterDaemon object'
        self.assertIsInstance(d, nparcel.ExporterDaemon, msg)

    @classmethod
    def tearDownClass(cls):
        pass
