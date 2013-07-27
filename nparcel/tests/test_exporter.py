import unittest2

import nparcel


class TestExporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._r = nparcel.Exporter()

    def test_init(self):
        """Initialise an Exporter object.
        """
        msg = 'Object is not an nparcel.Exporter'
        self.assertIsInstance(self._r, nparcel.Exporter, msg)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
