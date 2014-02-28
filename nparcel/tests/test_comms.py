import unittest2
import tempfile
import os
import datetime

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list)


class TestComms(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        conf = nparcel.B2CConfig()
        conf.set_config_file(os.path.join('nparcel',
                                          'conf',
                                          'nparceld.conf'))
        conf.parse_config()
        proxy = conf.proxy_string()
        cls._c = nparcel.Comms(proxy=proxy,
                               scheme=conf.proxy_scheme,
                               sms_api=conf.sms_api_kwargs,
                               email_api=conf.email_api_kwargs)
        cls._c.set_template_base('nparcel')
        cls._now = datetime.datetime.now()

        db = cls._c.db
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.agent, 'fixture': 'agents.py'},
                    {'db': db.job, 'fixture': 'jobs.py'},
                    {'db': db.jobitem, 'fixture': 'jobitems.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        # Update the returns created_ts.
        cls._now = str(datetime.datetime.now()).split('.')[0]
        sql = """UPDATE job_item
 SET created_ts = '%s'""" % cls._now
        db(sql)

        cls._c.db.commit()

    def test_init(self):
        """Initialise a Comms object.
        """
        msg = 'Object is not a nparcel.Comms'
        self.assertIsInstance(self._c, nparcel.Comms, msg)

    def test_send_sms_test(self):
        """Send test SMS.
        """
        dry = True

        details = {'phone_nbr': '0431602145'}

        received = self._c.send_sms(details,
                                    template='test',
                                    dry=dry)
        msg = 'Test SMS send should return True'
        self.assertTrue(received)

    def test_send_sms_reminder(self):
        """Send reminder SMS.
        """
        dry = True

        details = {'name': 'Mannum Newsagency',
                   'address': '77 Randwell Street',
                   'suburb': 'MANNUM',
                   'postcode': '5238',
                   'connote_nbr': 'connote_rem',
                   'item_nbr': 'item_nbr_rem',
                   'phone_nbr': '0431602145',
                   'date': '%s' % self._now.split('.')[0]}

        received = self._c.send_sms(details,
                                    template='rem',
                                    dry=dry)
        msg = 'Reminder SMS send should return True'
        self.assertTrue(received)

    def test_send_sms_primary_elect(self):
        """Send primary elect SMS.
        """
        dry = True

        details = {'name': 'Primary Elect Newsagency',
                   'address': '77 Primary Street',
                   'suburb': 'ELECT',
                   'postcode': '5238',
                   'connote_nbr': 'connote_nbr_pe',
                   'item_nbr': 'item_nbr_pe',
                   'phone_nbr': '0431602145'}

        received = self._c.send_sms(details,
                                    template='pe',
                                    dry=dry)
        msg = 'Primary Elect SMS send should return True'
        self.assertTrue(received)

    def test_send_sms_delay(self):
        """Send delayed delivery SMS.
        """
        dry = True

        details = {'name': 'Delay Newsagency',
                   'address': '10 Delay Street',
                   'suburb': 'Delayville',
                   'postcode': '3019',
                   'connote_nbr': 'connote_delay',
                   'item_nbr': 'item_nbr_delay',
                   'phone_nbr': '0431602145'}

        received = self._c.send_sms(details,
                                    template='delay',
                                    dry=dry)
        msg = 'Dealyed delivery SMS send should return True'
        self.assertTrue(received)

    def test_send_sms_loader(self):
        """Send loader SMS.
        """
        dry = True

        details = {'name': 'Loader Newsagency',
                   'address': '10 Loader Street',
                   'suburb': 'Loaderville',
                   'postcode': '3019',
                   'connote_nbr': 'connote_loader',
                   'item_nbr': 'item_nbr_loader',
                   'phone_nbr': '0431602145'}

        received = self._c.send_sms(details,
                                    template='body',
                                    dry=dry)
        msg = 'Loader SMS send should return True'
        self.assertTrue(received)

    def test_send_sms_returns(self):
        """Send returns SMS.
        """
        dry = True

        details = {'name': 'Returns Newsagency',
                   'address': '10 Returns Street',
                   'suburb': 'Returnsville',
                   'postcode': '3333',
                   'connote_nbr': 'returns_connote',
                   'item_nbr': 'returns_item',
                   'phone_nbr': '0431602145',
                   'returns_refs': 'ref1, ref2, ref3',
                   'date': '%s' % self._now.split('.')[0]}

        received = self._c.send_sms(details,
                                    template='ret',
                                    dry=dry)
        msg = 'Returns SMS send should return True'
        self.assertTrue(received)

    def test_get_return_date_string_based(self):
        """Create the return date -- string based.
        """
        date_str = '2013-09-19 08:52:13.308266'
        received = self._c.get_return_date(date_str)
        expected = 'Friday 27 September 2013'
        msg = 'Generated returned date error -- string input'
        self.assertEqual(received, expected, msg)

    def test_get_return_date_none(self):
        """Create the return date -- None.
        """
        date_str = None
        received = self._c.get_return_date(date_str)
        msg = 'Generated returned date error -- None'
        self.assertIsNone(received, msg)

    def test_get_return_date_datetime_based(self):
        """Create the return date -- datetime based.
        """
        date_datetime = datetime.datetime(2013, 9, 19, 8, 52, 13, 308266)
        received = self._c.get_return_date(date_datetime)
        expected = 'Friday 27 September 2013'
        msg = 'Generated returned date error -- datetime input'
        self.assertEqual(received, expected, msg)

    def test_send_email_test(self):
        """Send test email.
        """
        dry = True

        date = self._c.get_return_date(self._now)
        details = {'email_addr': 'loumar@tollgroup.com'}

        received = self._c.send_email(details,
                                      template='test',
                                      dry=dry)
        msg = 'Reminder email send should return True'
        self.assertTrue(received)

    def test_send_email_reminder(self):
        """Send reminder email comms.
        """
        dry = True

        date = self._c.get_return_date(self._now)
        details = {'name': 'Mannum Newsagency',
                   'address': '77 Randwell Street',
                   'suburb': 'MANNUM',
                   'postcode': '5238',
                   'connote_nbr': 'connote_1234',
                   'item_nbr': 'item_nbr_1234',
                   'email_addr': 'loumar@tollgroup.com',
                   'date': '%s' % date}

        received = self._c.send_email(details,
                                      template='rem',
                                      dry=dry)
        msg = 'Reminder email send should return True'
        self.assertTrue(received)

    def test_send_email_primary_elect(self):
        """Send primary elect email comms.
        """
        dry = True

        details = {'name': 'PE Newsagency',
                   'address': '77 Primary Elect Street',
                   'suburb': 'Primaryville',
                   'postcode': '5238',
                   'connote_nbr': 'connote_pe',
                   'item_nbr': 'item_nbr_pe',
                   'email_addr': 'loumar@tollgroup.com'}

        received = self._c.send_email(details,
                                      template='pe',
                                      dry=dry)
        msg = 'Primary elect email send should return True'
        self.assertTrue(received)

    def test_send_email_delay(self):
        """Send delayed delivery email comms.
        """
        dry = True

        details = {'name': 'Delayed Newsagency',
                   'address': '77 Delay Street',
                   'suburb': 'Delayville',
                   'postcode': '5238',
                   'connote_nbr': 'connote_delay',
                   'item_nbr': 'item_nbr_delay',
                   'email_addr': 'loumar@tollgroup.com'}

        received = self._c.send_email(details,
                                      template='delay',
                                      dry=dry)
        msg = 'Delay pickup email send should return True'
        self.assertTrue(received)

    def test_send_email_loader(self):
        """Send loader email comms.
        """
        dry = True

        details = {'name': 'Loader Newsagency',
                   'address': '77 Loader Street',
                   'suburb': 'Loadertown',
                   'postcode': '5238',
                   'connote_nbr': 'connote_loader',
                   'item_nbr': 'item_nbr_loader',
                   'email_addr': 'loumar@tollgroup.com'}

        received = self._c.send_email(details,
                                      template='body',
                                      dry=dry)
        msg = 'Loader email send should return True'
        self.assertTrue(received)

    def test_send_email_returns(self):
        """Send returns email comms.
        """
        dry = True

        details = {'name': 'Returns Newsagency',
                   'address': '10 Returns Street',
                   'suburb': 'Returnsville',
                   'postcode': '3333',
                   'connote_nbr': 'returns_connote',
                   'item_nbr': 'returns_item',
                   'phone_nbr': '0431602145',
                   'email_addr': 'loumar@tollgroup.com',
                   'returns_refs': 'ref1, ref2, ref3',
                   'date': '%s' % self._now.split('.')[0]}

        received = self._c.send_email(details,
                                      template='ret',
                                      dry=dry)
        msg = 'Returns email send should return True'
        self.assertTrue(received)

    def test_send_err_email_returns(self):
        """Send returns error email comms.
        """
        dry = True

        details = {'name': 'Returns Newsagency',
                   'address': '10 Returns Street',
                   'suburb': 'Returnsville',
                   'postcode': '3333',
                   'connote_nbr': 'returns_connote',
                   'item_nbr': 'returns_item',
                   'phone_nbr': '0431602145',
                   'email_addr': 'loumar@tollgroup.com',
                   'bad_email_addr': 'loumar@tollgroup.com',
                   'error_comms': 'email',
                   'returns_refs': 'ref1, ref2, ref3',
                   'date': '%s' % self._now.split('.')[0]}

        received = self._c.send_email(details,
                                      template='ret',
                                      err=True,
                                      dry=dry)
        msg = 'Returns error email send should return True'
        self.assertTrue(received)

    def test_process_loader(self):
        """Test processing -- loader.
        """
        dry = True

        files = ['email.1.body', 'sms.1.body',
                 'email.2.body', 'sms.2.body',
                 'email.6.body', 'sms.6.body']
        dodgy = ['banana', 'email.rem.3']

        dir = tempfile.mkdtemp()
        comms_files = []
        for f in files + dodgy:
            fh = open(os.path.join(dir, f), 'w')
            comms_files.append(fh.name)
            fh.close()

        for file in comms_files:
            received = self._c.process(file, dry=dry)
            msg = 'Loader comms files processing error'
            filename = os.path.basename(file)
            if (filename == 'email.2.body' or
                filename == 'sms.2.body' or
                filename == 'email.6.body' or
                filename == 'sms.6.body'):
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        # Cleanup.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._c.db.rollback()

    def test_process_loader_sms_error_comms(self):
        """Test processing -- loader SMS error comms.
        """
        dry = True

        files = ['email.6.body', 'sms.6.body']

        comms_files = []
        dir = tempfile.mkdtemp()
        for f in files:
            fh = open(os.path.join(dir, f), 'w')
            comms_files.append(fh.name)
            fh.close()

        # Provide a dodgy mobile.
        sql = """UPDATE job_item
SET phone_nbr = '0531602145'
WHERE id = 6"""
        self._c.db(sql)

        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'SMS error loader comms files processed incorrect'
            if os.path.basename(file) == 'email.6.body':
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        # Cleanup.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._c.db.rollback()

    def test_process_loader_email_error_comms(self):
        """Test processing -- loader email error comms.
        """
        dry = True

        files = ['email.6.body', 'sms.6.body']

        comms_files = []
        dir = tempfile.mkdtemp()
        for f in files:
            fh = open(os.path.join(dir, f), 'w')
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = 6"""
        self._c.db(sql)

        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'Email error loader comms files processed incorrect'
            if os.path.basename(file) == 'sms.6.body':
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        # Cleanup.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._c.db.rollback()

    def test_process_pe(self):
        """Test processing -- primary elect.
        """
        dry = True

        files = ['email.3.pe', 'sms.3.pe']

        dir = tempfile.mkdtemp()
        comms_files = []
        for f in files:
            fh = open(os.path.join(dir, f), 'w')
            comms_files.append(fh.name)
            fh.close()

        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'Primary elect comms files processed incorrect'
            self.assertTrue(received, msg)

        # Cleanup.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._c.db.rollback()

    def test_process_pe_sms_error_comms(self):
        """Test processing -- primary elect SMS error comms.
        """
        dry = True

        files = ['email.3.pe', 'sms.3.pe']

        dir = tempfile.mkdtemp()
        comms_files = []
        for f in files:
            fh = open(os.path.join(dir, f), 'w')
            comms_files.append(fh.name)
            fh.close()

        # Provide a dodgy mobile.
        sql = """UPDATE job_item
SET phone_nbr = '0531602145'
WHERE id = 3"""
        self._c.db(sql)

        for file in comms_files:
            received = self._c.process(file, dry=dry)
            msg = 'Primary Elect comms files processed incorrect'
            if os.path.basename(file) == 'email.3.pe':
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        # Cleanup.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._c.db.rollback()

    def test_process_pe_email_error_comms(self):
        """Test processing -- primary elect email error comms.
        """
        dry = True

        files = ['email.3.pe', 'sms.3.pe']

        dir = tempfile.mkdtemp()
        comms_files = []
        for f in files:
            fh = open(os.path.join(dir, f), 'w')
            comms_files.append(fh.name)
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = 3"""
        self._c.db(sql)

        for file in comms_files:
            received = self._c.process(file, dry=dry)
            msg = 'Primary Elect comms files processed incorrect'
            if os.path.basename(file) == 'sms.3.pe':
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        # Cleanup.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._c.db.rollback()

    def test_process_reminder(self):
        """Test processing -- reminder.
        """
        dry = True

        files = ['email.6.rem', 'sms.6.rem']

        dir = tempfile.mkdtemp()
        comms_files = []
        for f in files:
            fh = open(os.path.join(dir, f), 'w')
            comms_files.append(fh.name)
            fh.close()

        for file in comms_files:
            received = self._c.process(file, dry=dry)
            msg = 'Reminder comms files processed incorrect'
            self.assertTrue(received, msg)

        # Cleanup.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._c.db.rollback()

    def test_process_reminder_sms_error_comms(self):
        """Test processing -- SMS reminder error comms.
        """
        dry = True

        files = ['email.6.rem', 'sms.6.rem']

        dir = tempfile.mkdtemp()
        comms_files = []
        for f in files:
            fh = open(os.path.join(dir, f), 'w')
            comms_files.append(fh.name)
            fh.close()

        # Provide a dodgy mobile.
        sql = """UPDATE job_item
SET phone_nbr = '0531602145'
WHERE id = 6"""
        self._c.db(sql)

        for file in comms_files:
            received = self._c.process(file, dry=dry)
            msg = 'SMS errr reminder comms files processed incorrect'
            if os.path.basename(file) == 'email.6.rem':
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        # Cleanup.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._c.db.rollback()

    def test_process_reminder_email_error_comms(self):
        """Test processing -- reminder email error comms.
        """
        dry = True

        files = ['email.6.rem', 'sms.6.rem']

        dir = tempfile.mkdtemp()
        comms_files = []
        for f in files:
            fh = open(os.path.join(dir, f), 'w')
            comms_files.append(fh.name)
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = 6"""
        self._c.db(sql)

        for file in comms_files:
            received = self._c.process(file, dry=dry)
            msg = 'Email error reminder comms files processed incorrect'
            if os.path.basename(file) == 'sms.6.rem':
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        # Cleanup.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._c.db.rollback()

    def test_get_agent_details(self):
        """Verify agent details.
        """
        received = self._c.get_agent_details(6)
        expected = {'address': 'N031 Address',
                    'bu_id': 1,
                    'connote_nbr': 'uncollected_connote_sc_1',
                    'created_ts': '%s' % self._now,
                    'item_nbr': 'uncollected_connote_sc_1_item_nbr',
                    'email_addr': 'loumar@tollgroup.com',
                    'phone_nbr': '0431602145',
                    'name': 'N031 Name',
                    'postcode': '1234',
                    'suburb': 'N031 Suburb',
                    'pickup_ts': None}
        msg = 'job_item.id based Agent details incorrect'
        self.assertDictEqual(received, expected, msg)

    def test_parse_comms_filename(self):
        """Verify the parse_comms_filename.
        """
        received = self._c.parse_comms_filename('')
        expected = ()
        msg = 'Filename "" incorrect'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.parse_comms_filename('sms.333.pe')
        expected = ('sms', 333, 'pe')
        msg = 'Filename "sms.333.pe" incorrect'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.parse_comms_filename('sms.333.rem')
        expected = ('sms', 333, 'rem')
        msg = 'Filename "sms.333.rem" incorrect'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.parse_comms_filename('sms.333.body')
        expected = ('sms', 333, 'body')
        msg = 'Filename "sms.333.body" incorrect'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.parse_comms_filename('email.333.pe')
        expected = ('email', 333, 'pe')
        msg = 'Filename "email.333.pe" incorrect'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.parse_comms_filename('email.333.rem')
        expected = ('email', 333, 'rem')
        msg = 'Filename "email.333.rem" incorrect'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.parse_comms_filename('email.333.body')
        expected = ('email', 333, 'body')
        msg = 'Filename "email.333.body" incorrect'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.parse_comms_filename('email..pe')
        expected = ()
        msg = 'Filename "email..pe" incorrect'
        self.assertTupleEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._c = None
        del cls._c
        del cls._now
