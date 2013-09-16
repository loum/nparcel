import unittest2

import nparcel


class TestReminder(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._r = nparcel.Reminder()

    def test_init(self):
        """Initialise a Reminder object.
        """
        msg = 'Object is not a nparcel.Reminder'
        self.assertIsInstance(self._r, nparcel.Reminder, msg)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        del cls._r
