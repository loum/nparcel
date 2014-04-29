import unittest2
import os
import datetime

import nparcel


class TestReminderB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = nparcel.ReminderB2CConfig()

    def test_init(self):
        """Initialise a ReminderB2CConfig object.
        """
        msg = 'Object is not a nparcel.ReminderB2CConfig'
        self.assertIsInstance(self._c, nparcel.ReminderB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('nparcel', 'conf', 'top.conf')
        self._c.set_config_file(config_file)
        self._c.parse_config()

        received = self._c.reminder_loop
        expected = 3600
        msg = 'timeout.reminder_loop error'
        self.assertEqual(received, expected, msg)

        received = self._c.comms_dir
        expected = os.path.join(os.sep,
                                'data',
                                'nparcel',
                                'comms')
        msg = 'dir.comms error'
        self.assertEqual(received, expected, msg)

        received = self._c.notification_delay
        expected = 345600
        msg = 'reminder.notification_delay error'
        self.assertEqual(received, expected, msg)

        received = self._c.start_date
        expected = datetime.datetime(2013, 10, 9, 0, 0, 0)
        msg = 'reminder.start_date error'
        self.assertEqual(received, expected, msg)

        received = self._c.hold_period
        expected = 691200
        msg = 'reminder.hold_period error'
        self.assertEqual(received, expected, msg)

    def tearDown(self):
        del self._c
