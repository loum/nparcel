import unittest2

import nparcel


class TestParser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_init(self):
        """Initialise a Parser object.
        """
        p = nparcel.Parser()
        msg = 'Object is not an nparcel.Parser'
        self.assertIsInstance(p, nparcel.Parser, msg)

    @classmethod
    def tearDownClass(cls):
        pass
