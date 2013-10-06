import unittest2
import datetime

import nparcel


class TestReminderDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf_file = 'nparcel/conf/nparceld.conf'
        cls._rd = nparcel.ReminderDaemon(pidfile=None, config=conf_file)

    def test_init(self):
        """Intialise a ReminderDaemon object.
        """
        msg = 'Not a nparcel.ReminderDaemon object'
        self.assertIsInstance(self._rd, nparcel.ReminderDaemon, msg)

    def test_start(self):
        """Reminder _start processing loop.
        """
        self._rd.dry = True
        self._rd._start(self._rd.exit_event)

    def test_skip_day_is_a_skip_day(self):
        """Current skip day check.
        """
        # Fudge the configured skip days.
        fudge_day = datetime.datetime.now()
        self._rd.config.set_skip_days([fudge_day.strftime('%A')])
        received = self._rd._skip_day()
        msg = 'Is a skip day'
        self.assertTrue(received, msg)

    def test_skip_day_is_not_a_skip_day(self):
        """Non skip day check.
        """
        # Fudge the configured skip days.
        fudge_day = datetime.datetime.now() + datetime.timedelta(days=3)
        self._rd.config.set_skip_days([fudge_day.strftime('%A')])
        received = self._rd._skip_day()
        msg = 'Not a skip day'
        self.assertFalse(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._rd = None
        del cls._rd
