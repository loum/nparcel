import unittest2
import datetime
import os
import tempfile

import top
from top.utils.files import (remove_files,
                             get_directory_files_list)


class TestCommsDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        cls._cd = top.CommsDaemon(pidfile=None)
        cls._cd._config = top.CommsB2CConfig()

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
                           'loumar@tollgroup.com')
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
        # Only uncomment when you need to send real messages.  Leaving it
        # uncommented will break the tests.
        #cls._cd.config.add_section('proxy')
        #cls._cd.config.set('proxy', 'host', 'auproxy-farm.toll.com.au')
        #cls._cd.config.set('proxy', 'user', 'loumar')
        #cls._cd.config.set('proxy', 'password', '<passwd>')
        #cls._cd.config.set('proxy', 'port', '8080')
        #cls._cd.config.set('proxy', 'protocol', 'https')

        # Prod instance.
        cls._cd.config.set_prod('faswbaup02')

        # Call up front to pre-load the DB.
        cls._cd._comms = top.Comms(**(cls._cd.comms_kwargs))
        template_dir = os.path.join('top', 'templates')
        cls._cd._comms._emailer.set_template_base(template_dir)
        cls._cd._comms._smser.set_template_base(template_dir)
        cls._cd._emailer.set_template_base(template_dir)

        db = cls._cd._comms.db
        fixture_dir = os.path.join('top', 'tests', 'fixtures')
        fixtures = [{'db': db.agent, 'fixture': 'agents.py'},
                    {'db': db.job, 'fixture': 'jobs.py'},
                    {'db': db.jobitem, 'fixture': 'jobitems.py'},
                    {'db': db.returns_reference,
                     'fixture': 'returns_reference.py'},
                    {'db': db.returns, 'fixture': 'returns.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Initialise a CommsDaemon object.
        """
        msg = 'Not a top.CommsDaemon object'
        self.assertIsInstance(self._cd, top.CommsDaemon, msg)

    def test_start(self):
        """Start file processing loop.
        """
        # Change to False to actually send.  BE CAREFUL!
        dry = True

        old_dry = self._cd.dry
        old_file = self._cd.file
        old_comms_dir = self._cd.comms_dir
        old_send_time_ranges = list(self._cd.send_time_ranges)
        old_skip_days = list(self._cd.skip_days)
        old_controlled_templates = list(self._cd.controlled_templates)
        old_uncontrolled_templates = list(self._cd.uncontrolled_templates)

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
                       'email.2.ret',
                       'sms.2.ret',
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
        self._cd.set_uncontrolled_templates(['ret'])
        self._cd.comms.set_template_tokens(['body',
                                            'rem',
                                            'delay',
                                            'pe',
                                            'ret'])
        self._cd.comms.set_returns_template_tokens(['ret'])
        self._cd._start(self._cd.exit_event)

        # Clean up.
        self._cd._exit_event.clear()
        self._cd.set_dry(old_dry)
        self._cd.set_file(old_file)
        self._cd.set_comms_dir(old_comms_dir)
        self._cd.set_send_time_ranges(old_send_time_ranges)
        self._cd.set_skip_days(old_skip_days)
        self._cd.set_controlled_templates(old_controlled_templates)
        self._cd.set_uncontrolled_templates(old_uncontrolled_templates)
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
        subject = 'Warning - Comms message count was at %d' % count
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
        subject = 'Error - Comms message count was at %d' % count
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
        self._cd.set_comms_dir(old_comms_dir)
        remove_files(fs)
        os.removedirs(dir)

    def test_comms_kwargs_initialised_config(self):
        """Verify the comms kwarg initialiser structure -- test config.
        """
        received = self._cd.comms_kwargs
        expected = {'db': None,
                    'prod': None,
                    'email_api': {'api': self._email_api,
                                  'api_password': '<email_pw>',
                                  'api_username': '<email_user>',
                                  'support': 'loumar@tollgroup.com'},
                    'proxy': None,
                    'scheme': 'https',
                    'sms_api': {'api': self._sms_api,
                                'api_password': '<sms_pw>',
                                'api_username': '<sms_user>'},
                    'templates': [],
                    'returns_templates': []}
        msg = 'Comms kwargs initialiser with no config error'
        self.assertDictEqual(received, expected, msg)

    def test_comms_kwargs_no_config(self):
        """Verify the comms kwarg initialiser structure -- no config.
        """
        cd = top.CommsDaemon(pidfile=None)
        cd._config = top.CommsB2CConfig()

        received = cd.comms_kwargs
        expected = {'db': None,
                    'prod': None,
                    'email_api': {},
                    'proxy': None,
                    'scheme': 'https',
                    'sms_api': {},
                    'templates': [],
                    'returns_templates': []}
        msg = 'Comms kwargs initialiser with no config error'
        self.assertDictEqual(received, expected, msg)

    def test_comms_kwargs(self):
        """Verify the comms kwarg initialiser structure.
        """
        cd = top.CommsDaemon(pidfile=None)
        cd.config = top.CommsB2CConfig()

        # Environment.
        cd.config.set_prod('faswbaup02')

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

        # Templates.
        cd.config.set_controlled_templates(['body', 'rem', 'delay', 'pe'])
        cd.config.set_uncontrolled_templates(['ret'])

        received = cd.comms_kwargs
        expected = {'prod': 'faswbaup02',
                    'db': {'driver': 'FreeTDS',
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
                                'api_password': '<sms_pw>'},
                    'templates': ['body',
                                  'rem',
                                  'delay',
                                  'pe',
                                  'ret'],
                    'returns_templates': ['ret']}
        msg = 'Comms kwargs initialiser error'
        self.assertDictEqual(received, expected, msg)

    def test_comms_kwargs(self):
        """Verify the comms_kwargs property
        """
        received = self._cd.comms_kwargs
        sa = 'https://apps.cinder.co/tollgroup/wsemail/emailservice.svc/sendemail'
        ea = 'https://api.esendex.com/v1.0/messagedispatcher'
        expected = {'db': None,
                    'email_api': {'api': sa,
                                  'api_password': '<email_pw>',
                                  'api_username': '<email_user>',
                                  'support': 'loumar@tollgroup.com'},
                    'prod': None,
                    'proxy': None,
                    'returns_templates': [],
                    'scheme': 'https',
                    'sms_api': {'api': ea,
                                'api_password': '<sms_pw>',
                                'api_username': '<sms_user>'},
                                'templates': []}
        msg = 'comms_kwargs structure error'
        self.assertDictEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._cd.config.remove_section('db')
        cls._cd.config.remove_section('rest')
        cls._cd.config.remove_section('proxy')
        cls._cd.config.remove_section('environment')
        del cls._cd
        del cls._email_api
        del cls._sms_api
