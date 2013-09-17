import unittest2
import datetime

import nparcel


class TestReminder(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/conf/npreminder.conf'

    def setUp(self):
        self._r = nparcel.Reminder()

    def test_init(self):
        """Initialise a Reminder object.
        """
        msg = 'Object is not a nparcel.Reminder'
        self.assertIsInstance(self._r, nparcel.Reminder, msg)

    def test_assign_missing_config(self):
        """Assign missing config file.
        """
        msg = 'Missing config file should raise error'
        self.assertRaises(SystemExit,
                          self._r.config.set_config_file, 'dodgy')

    def test_config_items(self):
        """Verify config items.
        """
        self._r.config.set_config_file(self._file)
        self._r.parse_config()

        received = self._r.notification_delay
        expected = 345600
        msg = 'Configured notification delay error'
        self.assertEqual(received, expected, msg)

        received = self._r.start_date
        expected = datetime.datetime(2013, 9, 15, 0, 0, 0)
        msg = 'Configured start date error'
        self.assertEqual(received, expected, msg)

    def tearDown(self):
        self._r = None
        del self._r

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        del cls._file
