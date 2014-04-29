import unittest2

import top


class TestRest(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._r = top.Rest()

    def test_init(self):
        """Verify initialisation of an top.Rest object.
        """
        msg = 'Object is not an top.Rest'
        self.assertIsInstance(self._r, top.Rest, msg)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        del cls._r
