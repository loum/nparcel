import unittest2

import nparcel


class TestRest(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._r = nparcel.Rest()

    def test_init(self):
        """Verify initialisation of an nparcel.Rest object.
        """
        msg = 'Object is not an nparcel.Rest'
        self.assertIsInstance(self._r, nparcel.Rest, msg)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        del cls._r
