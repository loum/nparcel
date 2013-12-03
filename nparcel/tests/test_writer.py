import unittest2

import nparcel


class TestWriter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._w = nparcel.Writer()

    def test_init(self):
        """Initialise a Writer object.
        """
        msg = 'Object is not an nparcel.Writer'
        self.assertIsInstance(self._w, nparcel.Writer, msg)

    @classmethod
    def tearDownClass(cls):
        cls._w = None
        del cls._w
