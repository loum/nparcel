import unittest2

import nparcel

class TestMapper(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._m = nparcel.Mapper()

    def test_init(self):
        """Initialise a Mapper object.
        """
        msg = 'Object is not an nparcel.Mapper'
        self.assertIsInstance(self._m, nparcel.Mapper, msg)

    @classmethod
    def tearDownClass(cls):
        cls._m = None
        del cls._m
