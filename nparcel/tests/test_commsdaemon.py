import unittest2
import tempfile
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

    def test_within_time_ranges_outside_ranges(self):
        """Outside current time range.
        """
        self._cd._within_time_ranges()
        msg = 'Should not be inside time range'

    @classmethod
    def tearDownClass(cls):
        cls._cd = None
        del cls._cd
