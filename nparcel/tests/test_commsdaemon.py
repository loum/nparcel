import unittest2
import datetime
import os
import tempfile

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list)


class TestCommsDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        cls._cd = nparcel.CommsDaemon(pidfile=None)
        cls._cd.config = nparcel.CommsB2CConfig()

        # If you want to perform a real run, uncomment the following
        # according to your environment and provide the REST
        # interface/proxy credentials.
        # REST API.
        cls._email_api = ('%s://%s' %
        ('https',
         'apps.cinder.co/tollgroup/wsemail/emailservice.svc/sendemail'))
        cls._sms_api = ('%s://%s' %
                        ('https',
                         'api.esendex.com/v1.0/messagedispatcher'))
        cls._cd.config.add_section('rest')
        cls._cd.config.set('rest', 'email_api', cls._email_api)
        cls._cd.config.set('rest',
                           'email_user',
                           '<email_user>')
        cls._cd.config.set('rest',
                           'email_pw',
                           '<email_pw>')
        cls._cd.config.set('rest',
                           'failed_email',
                           'lou.markovski@gmail.com')
        cls._cd.config.set('rest',
                           'sms_api',
                           'https://api.esendex.com/v1.0/messagedispatcher')
        cls._cd.config.set('rest',
                           'sms_user',
                           '<sms_user>')
        cls._cd.config.set('rest',
                           'sms_pw',
                           '<sms_pw>')

        # Proxy.
        #cls._cd.config.add_section('proxy')
        #cls._cd.config.set('proxy', 'host', 'auproxy-farm.toll.com.au')
        #cls._cd.config.set('proxy', 'user', 'loumar')
        #cls._cd.config.set('proxy', 'password', '<passwd>')
        #cls._cd.config.set('proxy', 'port', '1442')
        #cls._cd.config.set('proxy', 'protocol', 'http')

        # Call up front to pre-load the DB.
        cls._cd._comms = nparcel.Comms(**(cls._cd.comms_kwargs))
        template_dir = os.path.join('nparcel', 'templates')
        cls._cd._comms._emailer.set_template_base(template_dir)
        cls._cd._comms._smser.set_template_base(template_dir)
        cls._cd._emailer.set_template_base(template_dir)

        db = cls._cd._comms.db
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.agent, 'fixture': 'agents.py'},
                    {'db': db.job, 'fixture': 'jobs.py'},
                    {'db': db.jobitem, 'fixture': 'jobitems.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Initialise a CommsDaemon object.
        """
        msg = 'Not a nparcel.CommsDaemon object'
        self.assertIsInstance(self._cd, nparcel.CommsDaemon, msg)

    def test_start(self):
        """Start file processing loop.
        """
        # Chamge to False to actually send.  BE CAREFUL!
        dry = True

        old_dry = self._cd.dry
        old_file = self._cd.file
        old_comms_dir = self._cd.comms_dir
        old_send_time_ranges = list(self._cd.send_time_ranges)
        old_skip_days = list(self._cd.skip_days)
        old_controlled_templates = list(self._cd.controlled_templates)

        # job_item 1 collected.
        # job_item 6 uncollected/no notify
        dir = tempfile.mkdtemp()
        event_files = ['email.1.body',
                       'sms.1.body',
                       'email.3.pe',
                       'sms.3.pe',
                       'email.6.body',
                       'sms.6.body',
                       'email.6.rem',
                       'sms.6.rem',
                       'email.9.delay',
                       'sms.9.delay',
                       'email.9999999.body.err',
                       'sms.9999999.body.err']
        for f in event_files:
            fh = open(os.path.join(dir, f), 'w')
            fh.close()

        # Start processing.
        self._cd.set_dry(dry)
        if not dry:
            self._cd.set_batch()
        self._cd.set_file()
        self._cd.set_comms_dir(dir)
        self._cd.set_send_time_ranges(None)
        self._cd.set_skip_days(None)
        self._cd.set_controlled_templates(['body',
                                           'rem',
                                           'delay',
                                           'pe'])
        self._cd._start(self._cd.exit_event)

        # Clean up.
        self._cd._exit_event.clear()
        self._cd.set_dry(old_dry)
        self._cd.set_file(old_file)
        self._cd.set_comms_dir(old_comms_dir)
        self._cd.set_send_time_ranges(old_send_time_ranges)
        self._cd.set_skip_days(old_skip_days)
        self._cd.set_controlled_templates(old_controlled_templates)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    def test_skip_day_is_a_skip_day(self):
        """Current skip day check.
        """
        # Fudge the configured skip days.
        old_skip_days = list(self._cd.skip_days)

        fudge_day = datetime.datetime.now()
        self._cd.set_skip_days([fudge_day.strftime('%A')])
        received = self._cd._skip_day()
        msg = 'Is a skip day'
        self.assertTrue(received, msg)

        # Cleanup.
        self._cd.set_skip_days(old_skip_days)

    def test_skip_day_is_not_a_skip_day(self):
        """Non skip day check.
        """
        # Fudge the configured skip days.
        old_skip_days = list(self._cd.skip_days)

        fudge_day = datetime.datetime.now() + datetime.timedelta(days=3)
        self._cd.set_skip_days([fudge_day.strftime('%A')])
        received = self._cd._skip_day()
        msg = 'Not a skip day'
        self.assertFalse(received, msg)

        # Cleanup.
        self._cd.set_skip_days(old_skip_days)

    def test_within_time_ranges_within_ranges(self):
        """Within configured time range.
        """
        # Fudge the configured skip days.
        old_ranges = list(self._cd.send_time_ranges)

        current_dt = datetime.datetime.now()
        range_dt = current_dt - datetime.timedelta(seconds=3600)
        fudge_range = '%s-23:59' % range_dt.strftime('%H:%M')
        self._cd.set_send_time_ranges([fudge_range])

        received = self._cd._within_time_ranges()
        msg = 'Should not be inside time range'
        self.assertTrue(received, msg)

        # Cleanup.
        self._cd.set_send_time_ranges(old_ranges)

    def test_within_time_ranges_outside_ranges(self):
        """Outside configured time range.
        """
        # Fudge the configured skip days.
        old_ranges = list(self._cd.send_time_ranges)

        current_dt = datetime.datetime.now()
        range_dt = current_dt + datetime.timedelta(seconds=60)
        fudge_range = '%s-23:59' % range_dt.strftime('%H:%M')
        self._cd.set_send_time_ranges([fudge_range])

        received = self._cd._within_time_ranges()
        msg = 'Should be inside time range'
        self.assertFalse(received, msg)

        # Cleanup.
        self._cd.set_send_time_ranges(old_ranges)

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
             'warning_threshold': self._cd.q_warning}
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
             'error_threshold': self._cd.q_error}
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

    def test_comms_kwargs_no_config(self):
        """Verify the comms kwarg initialiser structure -- no config.
        """
        received = self._cd.comms_kwargs
        expected = {'db': None,
                    'email_api': {'api': self._email_api,
                                  'api_password': '<email_pw>',
                                  'api_username': '<email_user>',
                                  'support': 'lou.markovski@gmail.com'},
                    'proxy': None,
                    'scheme': 'https',
                    'sms_api': {'api': self._sms_api,
                                'api_password': '<sms_pw>',
                                'api_username': '<sms_user>'}}
        msg = 'Comms kwargs initialiser with no config error'
        self.assertDictEqual(received, expected, msg)

    def test_comms_kwargs(self):
        """Verify the comms kwarg initialiser structure.
        """
        # Proxy kwargs.
        cd = nparcel.CommsDaemon(pidfile=None)
        cd.config = nparcel.B2CConfig()

        # DB.
        cd.config.add_section('db')
        cd.config.set('db', 'driver', 'FreeTDS')
        cd.config.set('db', 'host', 'SQVDBAUT07')
        cd.config.set('db', 'database', 'Nparcel')
        cd.config.set('db', 'user', 'user')
        cd.config.set('db', 'password', '<db_passwd>')
        cd.config.set('db', 'port', '1442')

        # REST API.
        cd.config.add_section('rest')
        cd.config.set('rest', 'email_api', 'https://apps.cinder.co')
        cd.config.set('rest', 'email_user', 'username')
        cd.config.set('rest', 'email_pw', '<passwd>')
        cd.config.set('rest', 'failed_email', 'loumar@tollgroup.com')
        cd.config.set('rest', 'sms_api', 'https://api.esendex.com')
        cd.config.set('rest', 'sms_user', 'sms_user')
        cd.config.set('rest', 'sms_pw', '<sms_pw>')

        # Proxy.
        cd.config.add_section('proxy')
        cd.config.set('proxy', 'host', 'auproxy-farm.toll.com.au')
        cd.config.set('proxy', 'user', 'loumar')
        cd.config.set('proxy', 'password', '<passwd>')
        cd.config.set('proxy', 'port', '1442')
        cd.config.set('proxy', 'protocol', 'http')
        proxy = 'loumar:<passwd>@auproxy-farm.toll.com.au:1442'

        received = cd.comms_kwargs
        expected = {'db': {'driver': 'FreeTDS',
                           'host': 'SQVDBAUT07',
                           'database': 'Nparcel',
                           'user': 'user',
                           'password': '<db_passwd>',
                           'port': 1442},
                    'email_api': {'api': 'https://apps.cinder.co',
                                  'api_username': 'username',
                                  'api_password': '<passwd>',
                                  'support': 'loumar@tollgroup.com'},
                    'proxy': proxy,
                    'scheme': 'http',
                    'sms_api': {'api': 'https://api.esendex.com',
                                'api_username': 'sms_user',
                                'api_password': '<sms_pw>'}}
        msg = 'Comms kwargs initialiser error'
        self.assertDictEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._cd = None
        del cls._cd
        del cls._email_api
        del cls._sms_api
