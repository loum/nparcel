import unittest2

import nparcel


class TestAgedParcelReporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._agpr = nparcel.AgedParcelReporter()

    def test_init(self):
        """AgedParcelReporter initialisation placeholder.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        cls._agpr = None
