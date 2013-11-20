import unittest2

import nparcel


class TestTransSend(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._transsend = nparcel.TransSend()

    def test_init(self):
        """TransSend table initialisation.
        """
        msg = 'Object is not a TransSend instance'
        self.assertIsInstance(self._transsend, nparcel.TransSend, msg)

    @classmethod
    def tearDownClass(cls):
        cls._transsend = None
        del cls._transsend
