import unittest2
import datetime
import os
import tempfile

import nparcel
from nparcel.utils.files import remove_files


class TestCommsDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf_file = os.path.join('nparcel', 'conf', 'nparceld.conf')
        cls._cd = nparcel.CommsDaemon(pidfile=None, config=conf_file)
        cls._cd.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))

    def test_init(self):
        """Initialise a CommsDaemon object.
        """
        msg = 'Not a nparcel.CommsDaemon object'
        self.assertIsInstance(self._cd, nparcel.CommsDaemon, msg)

    def test_start(self):
        """Start file processing loop.
        """
        self._cd.set_dry()
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

    def test_message_queue_within_thresholds(self):
        """Message queue threshold check.
        """
        dry = True
        received = self._cd._message_queue_ok(0, dry=dry)
        msg = 'Message queue within threshold should return True'
        self.assertTrue(received, msg)

    def test_message_queue_within_thresholds_warning(self):
        """Message queue threshold check -- warning.
        """
        dry = True
        received = self._cd._message_queue_ok(100, dry=dry)
        msg = 'Message queue within threshold should return True'
        self.assertTrue(received, msg)

        received = self._cd._message_queue_ok(101, dry=dry)
        msg = 'Message queue above warning threshold should return True'
        self.assertTrue(received, msg)

    def test_message_queue_within_thresholds_error(self):
        """Message queue threshold check -- error.
        """
        dry = True
        received = self._cd._message_queue_ok(1000, dry=dry)
        msg = 'Message queue within warning threshold should return True'
        self.assertTrue(received, msg)

        received = self._cd._message_queue_ok(1001, dry=dry)
        msg = 'Message queue above error threshold should return True'
        self.assertFalse(received, msg)

    def test_message_queue_alert_email_warning(self):
        """Message queue alert email -- warning.
        """
        dry = True
        count = 101
        subject = 'Warning - Nparcel Comms message count was at %d' % count
        d = {'count': count,
             'date': datetime.datetime.now().strftime('%c'),
             'warning_threshold': self._cd.config.comms_q_warning}
        mime = self._cd.emailer.create_comms(subject=subject,
                                             data=d,
                                             template='message_q_warn')
        self._cd.emailer.set_recipients(['loumar@tollgroup.com'])
        received = self._cd.emailer.send(mime_message=mime, dry=dry)

    def test_message_queue_alert_email_error(self):
        """Message queue alert email -- error.
        """
        dry = True
        count = 1001
        subject = 'Error - Nparcel Comms message count was at %d' % count
        d = {'count': count,
             'date': datetime.datetime.now().strftime('%c'),
             'error_threshold': self._cd.config.comms_q_error}
        mime = self._cd.emailer.create_comms(subject=subject,
                                             data=d,
                                             template='message_q_err')
        self._cd.emailer.set_recipients(['loumar@tollgroup.com'])
        received = self._cd.emailer.send(mime_message=mime, dry=dry)

    def test_comms_file_not_set(self):
        """Get files from comms dir when attribute is not set.
        """
        old_comms_dir = self._cd.comms_dir
        self._cd.set_comms_dir(None)

        received = self._cd.get_comms_files()
        expected = []
        msg = 'Unset comms_dir should return empty list'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._cd.set_comms_dir(old_comms_dir)

    def test_comms_file_missing_directory(self):
        """Get files from missing comms dir.
        """
        old_comms_dir = self._cd.comms_dir
        dir = tempfile.mkdtemp()
        self._cd.set_comms_dir(dir)
        os.removedirs(dir)

        received = self._cd.get_comms_files()
        expected = []
        msg = 'Unset comms_dir should return empty list'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._cd.set_comms_dir(old_comms_dir)

    def test_comms_file_read(self):
        """Get comms files.
        """
        old_comms_dir = self._cd.comms_dir
        dir = tempfile.mkdtemp()
        self._cd.set_comms_dir(dir)

        comms_files = ['email.1.rem',
                       'sms.1.rem',
                       'email.1111.pe',
                       'sms.1111.pe',
                       'email.1234.delay',
                       'sms.1234.delay']
        dodgy = ['banana', 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._cd.comms_dir, f), 'w')
            fh.close()

        received = self._cd.get_comms_files()
        expected = [os.path.join(self._cd.comms_dir, x) for x in comms_files]
        msg = 'Unset comms_dir should return empty list'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        files_to_delete = comms_files + dodgy
        fs = [os.path.join(self._cd.comms_dir, x) for x in files_to_delete]
        remove_files(fs)
        self._cd.set_comms_dir(old_comms_dir)

    @classmethod
    def tearDownClass(cls):
        cls._cd = None
        del cls._cd
