import unittest2

import nparcel


class TestStopParser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._sp = nparcel.StopParser()

    def test_init(self):
        """Initialise a StopParser object.
        """
        sp = nparcel.StopParser()
        msg = 'Object is not an nparcel.StopParser'
        self.assertIsInstance(sp, nparcel.StopParser, msg)

    @classmethod
    def tearDownClass(cls):
        cls._sp = None
        del cls._sp
