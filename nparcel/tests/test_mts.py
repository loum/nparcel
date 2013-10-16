import unittest2

import nparcel


class TestMts(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._mts = nparcel.Mts(config='nparcel/conf/npmts.conf')

    def test_init(self):
        """Initialise a MTS object.
        """
        msg = 'Object is not an nparcel.Mts'
        self.assertIsInstance(self._mts, nparcel.Mts, msg)

    @classmethod
    def tearUpClass(cls):
        cls._mts = None
        del cls._mts
