import unittest2

import nparcel


class TestLoader(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_init(self):
        """Initialise a Loader object.
        """
        l = nparcel.Loader()
        msg = 'Object is not an nparcel.Loader'
        self.assertIsInstance(l, nparcel.Loader, msg)

    @classmethod
    def tearDownClass(cls):
        pass
