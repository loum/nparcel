import unittest2

import nparcel


class TestFilter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._f = nparcel.Filter()

    def test_init(self):
        """Initialise a Filter object.
        """
        msg = 'Object is not an nparcel.Filter'
        self.assertIsInstance(self._f, nparcel.Filter, msg)

    @classmethod
    def tearDownClass(cls):
        cls._f = None
        del cls._f
