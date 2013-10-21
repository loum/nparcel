import unittest2
import tempfile
import os
import datetime

import nparcel
from nparcel.utils.files import remove_files


class TestComms(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf = nparcel.B2CConfig()
        conf.set_config_file('nparcel/conf/nparceld.conf')
        conf.parse_config()
        proxy = conf.proxy_string()
        cls._comms_dir = tempfile.mkdtemp()
        cls._c = nparcel.Comms(proxy=proxy,
                               scheme=conf.proxy_scheme,
                               sms_api=conf.sms_api_kwargs,
                               email_api=conf.email_api_kwargs,
                               comms_dir=cls._comms_dir)
        cls._c.set_template_base('nparcel')
        cls._now = datetime.datetime.now()

        agents = [{'code': 'V031',
                   'state': 'VIC',
                   'name': 'V031 Name',
                   'address': 'V031 Address',
                   'postcode': '1234',
                   'suburb': 'V031 Suburb'},
                  {'code': 'N100',
                   'state': 'NSW',
                   'name': 'N100 Name',
                   'address': 'N100 Address',
                   'postcode': '2100',
                   'suburb': 'N100 Suburb'}]
        sql = cls._c.db._agent.insert_sql(agents[0])
        agent_01 = cls._c.db.insert(sql)
        sql = cls._c.db._agent.insert_sql(agents[1])
        agent_02 = cls._c.db.insert(sql)

        cls._now = datetime.datetime.now()
        jobs = [{'agent_id': agent_01,
                 'job_ts': '%s' % cls._now,
                 'bu_id': 1}]
        sql = cls._c.db.job.insert_sql(jobs[0])
        job_01 = cls._c.db.insert(sql)

        jobitems = [{'connote_nbr': 'con_001',
                     'item_nbr': 'item_nbr_001',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_01,
                     'created_ts': '%s' % cls._now},
                    {'connote_nbr': 'con_002',
                     'item_nbr': 'item_nbr_002',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_01,
                     'created_ts': '%s' % cls._now,
                     'pickup_ts': '%s' % cls._now}]
        sql = cls._c.db.jobitem.insert_sql(jobitems[0])
        cls._id_000 = cls._c.db.insert(sql)
        sql = cls._c.db.jobitem.insert_sql(jobitems[1])
        cls._id_001 = cls._c.db.insert(sql)

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

        date = self._c.get_return_date(self._now)
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

        date = self._c.get_return_date(self._now)
        details = {'name': 'Mannum Newsagency',
                   'address': '77 Randwell Street',
                   'suburb': 'MANNUM',
                   'postcode': '5238',
                   'connote_nbr': 'connote_rem',
                   'item_nbr': 'item_nbr_rem',
                   'phone_nbr': '0431602145',
                   'date': '%s' % date}

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

    def test_comms_file_not_set(self):
        """Get files from comms dir when attribute is not set.
        """
        old_comms_dir = self._c.comms_dir
        self._c.set_comms_dir(None)

        received = self._c.get_comms_files()
        expected = []
        msg = 'Unset comms_dir should return empty list'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.set_comms_dir(old_comms_dir)

    def test_comms_file_missing_directory(self):
        """Get files from missing comms dir.
        """
        old_comms_dir = self._c.comms_dir
        dir = tempfile.mkdtemp()
        self._c.set_comms_dir(dir)
        os.removedirs(dir)

        received = self._c.get_comms_files()
        expected = []
        msg = 'Unset comms_dir should return empty list'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.set_comms_dir(old_comms_dir)

    def test_comms_file_read(self):
        """Get comms files.
        """
        comms_files = ['email.1.rem',
                       'sms.1.rem',
                       'email.1111.pe',
                       'sms.1111.pe']
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        received = self._c.get_comms_files()
        expected = [os.path.join(self._c.comms_dir, x) for x in comms_files]
        msg = 'Unset comms_dir should return empty list'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        files_to_delete = comms_files + dodgy
        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_process_loader(self):
        """Test processing -- loader.
        """
        dry = True

        comms_files = ['%s.%d.body' % ('email', self._id_000),
                       '%s.%d.body' % ('sms', self._id_000),
                       '%s.%d.body' % ('email', self._id_001),
                       '%s.%d.body' % ('sms', self._id_001)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        files = self._c.get_comms_files()
        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'Loader comms files processed incorrect'
            filename = os.path.basename(file)
            if (filename == ('%s.%d.body' % ('email', self._id_000)) or
                filename == ('%s.%d.body' % ('sms', self._id_000))):
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        if not dry:
            received = self._c.get_comms_files()
            expected = []
            msg = 'Loader comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files
        else:
            files_to_delete.append('email.2.body.err')
            files_to_delete.append('sms.2.body.err')

        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_process_loader_sms_error_comms(self):
        """Test processing -- loader SMS error comms.
        """
        dry = True

        comms_files = ['%s.%d.body' % ('email', self._id_000),
                       '%s.%d.body' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        error_file = '%s.%d.body' % ('sms', self._id_000)
        valid_file = '%s.%d.body' % ('email', self._id_000)
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy mobile.
        sql = """UPDATE job_item
SET phone_nbr = '0531602145'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        files = self._c.get_comms_files()
        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'SMS error loader comms files processed incorrect'
            if file == os.path.join(self._c.comms_dir, valid_file):
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        if not dry:
            received = self._c.get_comms_files()
            expected = []
            msg = 'Loader comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files
        else:
            files_to_delete.append('%s.%d.%s.err' %
                                   ('sms', self._id_000, 'body'))

        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_process_loader_email_error_comms(self):
        """Test processing -- loader email error comms.
        """
        dry = True

        comms_files = ['%s.%d.body' % ('email', self._id_000),
                       '%s.%d.body' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        error_file = '%s.%d.body' % ('email', self._id_000)
        valid_file = '%s.%d.body' % ('sms', self._id_000)
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        files = self._c.get_comms_files()
        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'Email error loader comms files processed incorrect'
            if file == os.path.join(self._c.comms_dir, valid_file):
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        if not dry:
            received = self._c.get_comms_files()
            expected = []
            msg = 'Email error loader comms files second pass incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files
        else:
            files_to_delete.append('%s.%d.%s.err' %
                                   ('email', self._id_000, 'body'))

        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_process_pe(self):
        """Test processing -- primary elect.
        """
        dry = True

        comms_files = ['%s.%d.pe' % ('email', self._id_000),
                       '%s.%d.pe' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        files = self._c.get_comms_files()
        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'Primary elect comms files processed incorrect'
            self.assertTrue(received, msg)

        if not dry:
            received = self._c.get_comms_files()
            expected = []
            msg = 'Primary elect comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files

        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_process_pe_sms_error_comms(self):
        """Test processing -- primary elect SMS error comms.
        """
        dry = True

        comms_files = ['%s.%d.pe' % ('email', self._id_000),
                       '%s.%d.pe' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        error_file = '%s.%d.pe' % ('sms', self._id_000)
        valid_file = '%s.%d.pe' % ('email', self._id_000)
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy mobile.
        sql = """UPDATE job_item
SET phone_nbr = '0531602145'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        files = self._c.get_comms_files()
        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'Loader comms files processed incorrect'
            if file == os.path.join(self._c.comms_dir, valid_file):
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        if not dry:
            received = self._c.get_comms_files()
            expected = []
            msg = 'Primary elect comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files
        else:
            files_to_delete.append('%s.%d.%s.err' %
                                   ('sms', self._id_000, 'pe'))

        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_process_pe_email_error_comms(self):
        """Test processing -- primary elect email error comms.
        """
        dry = True

        comms_files = ['%s.%d.pe' % ('email', self._id_000),
                       '%s.%d.pe' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        error_file = '%s.%d.pe' % ('email', self._id_000)
        valid_file = '%s.%d.pe' % ('sms', self._id_000)
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        files = self._c.get_comms_files()
        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'Email error primary elect comms files processed incorrect'
            if file == os.path.join(self._c.comms_dir, valid_file):
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        if not dry:
            received = self._c.get_comms_files()
            expected = []
            msg = 'Email primary elect comms files second pass incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files
        else:
            files_to_delete.append('%s.%d.%s.err' %
                                   ('email', self._id_000, 'pe'))

        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_process_reminder(self):
        """Test processing -- reminder.
        """
        dry = True

        comms_files = ['%s.%d.rem' % ('email', self._id_000),
                       '%s.%d.rem' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        files = self._c.get_comms_files()
        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'Reminder comms files processed incorrect'
            self.assertTrue(received, msg)

        if not dry:
            received = self._c.get_comms_files()
            expected = []
            msg = 'Reminder comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files

        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_process_reminder_sms_error_comms(self):
        """Test processing -- SMS reminder error comms.
        """
        dry = True

        comms_files = ['%s.%d.rem' % ('email', self._id_000),
                       '%s.%d.rem' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        error_file = '%s.%d.rem' % ('sms', self._id_000)
        valid_file = '%s.%d.rem' % ('email', self._id_000)
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy mobile.
        sql = """UPDATE job_item
SET phone_nbr = '0531602145'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        files = self._c.get_comms_files()
        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'SMS errr reminder comms files processed incorrect'
            if file == os.path.join(self._c.comms_dir, valid_file):
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        if not dry:
            received = self._c.get_comms_files()
            expected = []
            msg = 'SMS error reminder comms files second pass incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files
        else:
            files_to_delete.append('%s.%d.%s.err' %
                                   ('sms', self._id_000, 'rem'))

        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_process_reminder_email_error_comms(self):
        """Test processing -- reminder email error comms.
        """
        dry = True

        comms_files = ['%s.%d.rem' % ('email', self._id_000),
                       '%s.%d.rem' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        error_file = '%s.%d.rem' % ('email', self._id_000)
        valid_file = '%s.%d.rem' % ('sms', self._id_000)
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        files = self._c.get_comms_files()
        for file in files:
            received = self._c.process(file, dry=dry)
            msg = 'Email error reminder comms files processed incorrect'
            if file == os.path.join(self._c.comms_dir, valid_file):
                self.assertTrue(received, msg)
            else:
                self.assertFalse(received, msg)

        if not dry:
            received = self._c.get_comms_files()
            expected = []
            msg = 'Email error reminder comms files second pass incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files
        else:
            files_to_delete.append('%s.%d.%s.err' %
                                   ('email', self._id_000, 'rem'))

        fs = [os.path.join(self._c.comms_dir, x) for x in files_to_delete]
        remove_files(fs)

    def test_get_agent_details(self):
        """Verify agent details.
        """
        received = self._c.get_agent_details(self._id_000)
        expected = {'address': 'V031 Address',
                    'connote_nbr': 'con_001',
                    'created_ts': '%s' % self._now,
                    'item_nbr': 'item_nbr_001',
                    'email_addr': 'loumar@tollgroup.com',
                    'phone_nbr': '0431602145',
                    'name': 'V031 Name',
                    'postcode': '1234',
                    'suburb': 'V031 Suburb',
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
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
        del cls._now
        del cls._id_000
