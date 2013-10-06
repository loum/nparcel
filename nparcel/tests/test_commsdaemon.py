import unittest2
import datetime

import nparcel


class TestCommsDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf_file = 'nparcel/conf/nparceld.conf'
        cls._cd = nparcel.CommsDaemon(pidfile=None, config=conf_file)

    def test_init(self):
        """Initialise a CommsDaemon object.
        """
        msg = 'Not a nparcel.CommsDaemon object'
        self.assertIsInstance(self._cd, nparcel.CommsDaemon, msg)

    def test_start(self):
        """Start file processing loop.
        """
        self._cd.dry = True
        self._cd._start(self._cd.exit_event)

    def test_skip_day_is_a_skip_day(self):
        """Current skip day check.
        """
        # Fudge the configured skip days.
        old_skip_days = list(self._cd.config.skip_days)
        fudge_day = datetime.datetime.now()
        self._cd.config.set_skip_days([fudge_day.strftime('%A')])
        received = self._cd._skip_day()
        msg = 'Is a skip day'
        self.assertTrue(received, msg)

        # Cleanup.
        self._cd.config.set_skip_days(old_skip_days)

    def test_skip_day_is_not_a_skip_day(self):
        """Non skip day check.
        """
        # Fudge the configured skip days.
        old_skip_days = list(self._cd.config.skip_days)
        fudge_day = datetime.datetime.now() + datetime.timedelta(days=3)
        self._cd.config.set_skip_days([fudge_day.strftime('%A')])
        received = self._cd._skip_day()
        msg = 'Not a skip day'
        self.assertFalse(received, msg)

        # Cleanup.
        self._cd.config.set_skip_days(old_skip_days)

    def test_within_time_ranges_within_ranges(self):
        """Within configured time range.
        """
        # Fudge the configured skip days.
        old_ranges = list(self._cd.config.send_time_ranges)
        current_dt = datetime.datetime.now()
        range_dt = current_dt - datetime.timedelta(seconds=3600)
        fudge_range = '%s-23:59' % range_dt.strftime('%H:%M')
        self._cd.config.set_send_time_ranges([fudge_range])

        received = self._cd._within_time_ranges()
        msg = 'Should not be inside time range'
        self.assertTrue(received, msg)

        # Cleanup.
        self._cd.config.set_send_time_ranges(old_ranges)

    def test_within_time_ranges_outside_ranges(self):
        """Outside configured time range.
        """
        # Fudge the configured skip days.
        old_ranges = list(self._cd.config.send_time_ranges)
        current_dt = datetime.datetime.now()
        range_dt = current_dt + datetime.timedelta(seconds=3600)
        fudge_range = '%s-23:59' % range_dt.strftime('%H:%M')
        self._cd.config.set_send_time_ranges([fudge_range])

        received = self._cd._within_time_ranges()
        msg = 'Should be inside time range'
        self.assertFalse(received, msg)

        # Cleanup.
        self._cd.config.set_send_time_ranges(old_ranges)

    @classmethod
    def tearDownClass(cls):
        cls._cd = None
        del cls._cd
