import unittest2

import nparcel


class TestCache(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._c = nparcel.Cache()

    def test_init(self):
        """Initialise a Cache object.
        """
        msg = "Object is not an nparcel.Cache()"
        self.assertIsInstance(self._c, nparcel.Cache, msg)

    @classmethod
    def tearDownClass(cls):
        cls._c = None
