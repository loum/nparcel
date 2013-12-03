import unittest2

import nparcel


class TestAuditer(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._a = nparcel.Auditer()

    def test_init(self):
        """Initialise a Auditer object.
        """
        msg = 'Object is not an nparcel.Auditer'
        self.assertIsInstance(self._a, nparcel.Auditer, msg)

    @classmethod
    def tearDownClass(cls):
        cls._a = None
        del cls._a
