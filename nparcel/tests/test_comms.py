import unittest2
import tempfile
import os
import datetime

import nparcel


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
                     'created_ts': '%s' % cls._now}]
        sql = cls._c.db.jobitem.insert_sql(jobitems[0])
        cls._id_000 = cls._c.db.insert(sql)

        cls._c.db.commit()

    def test_init(self):
        """Initialise a Comms object.
        """
        msg = 'Object is not a nparcel.Comms'
        self.assertIsInstance(self._c, nparcel.Comms, msg)

    def test_send_sms_test(self):
        """Send test SMS.
        """
        date = self._c.get_return_date(self._now)
        details = {'phone_nbr': '0431602145'}

        received = self._c.send_sms(details,
                                    template='test',
                                    dry=True)
        msg = 'Test SMS send should return True'
        self.assertTrue(received)

    def test_send_sms_reminder(self):
        """Send reminder SMS.
        """
        date = self._c.get_return_date(self._now)
        details = {'name': 'Mannum Newsagency',
                   'address': '77 Randwell Street',
                   'suburb': 'MANNUM',
                   'postcode': '5238',
                   'item_nbr': 'item_nbr_1234',
                   'phone_nbr': '0431602145',
                   'date': '%s' % date}

        received = self._c.send_sms(details,
                                    template='rem',
                                    dry=True)
        msg = 'Reminder SMS send should return True'
        self.assertTrue(received)

    def test_send_sms_primary_elect(self):
        """Send primary elect SMS.
        """
        details = {'name': 'Primary Elect Newsagency',
                   'address': '77 Primary Street',
                   'suburb': 'ELECT',
                   'postcode': '5238',
                   'item_nbr': 'item_nbr_pe',
                   'phone_nbr': '0431602145'}

        received = self._c.send_sms(details,
                                    template='pe',
                                    dry=True)
        msg = 'Primary Elect SMS send should return True'
        self.assertTrue(received)

    def test_send_sms_loader(self):
        """Send loader SMS.
        """
        details = {'name': 'Loader Newsagency',
                   'address': '10 Loader Street',
                   'suburb': 'Loaderville',
                   'postcode': '3019',
                   'item_nbr': 'item_nbr_loader',
                   'phone_nbr': '0431602145'}

        received = self._c.send_sms(details,
                                    template='body',
                                    dry=True)
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
        date = self._c.get_return_date(self._now)
        details = {'email_addr': 'loumar@tollgroup.com'}

        received = self._c.send_email(details,
                                      template='test',
                                      dry=True)
        msg = 'Reminder email send should return True'
        self.assertTrue(received)

    def test_send_email_reminder(self):
        """Send reminder email comms.
        """
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
                                      dry=True)
        msg = 'Reminder email send should return True'
        self.assertTrue(received)

    def test_send_email_primary_elect(self):
        """Send primary elect email comms.
        """
        details = {'name': 'PE Newsagency',
                   'address': '77 Primary Elect Street',
                   'suburb': 'Primaryville',
                   'postcode': '5238',
                   'connote_nbr': 'connote_pe',
                   'item_nbr': 'item_nbr_pe',
                   'email_addr': 'loumar@tollgroup.com'}

        received = self._c.send_email(details,
                                      template='pe',
                                      dry=True)
        msg = 'Primary elect email send should return True'
        self.assertTrue(received)

    def test_send_email_loader(self):
        """Send loader email comms.
        """
        details = {'name': 'Loader Newsagency',
                   'address': '77 Loader Street',
                   'suburb': 'Loadertown',
                   'postcode': '5238',
                   'connote_nbr': 'connote_loader',
                   'item_nbr': 'item_nbr_loader',
                   'email_addr': 'loumar@tollgroup.com'}

        received = self._c.send_email(details,
                                      template='body',
                                      dry=True)
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
        for f in comms_files + dodgy:
            os.remove(os.path.join(self._c.comms_dir, f))

    def test_process_loader(self):
        """Test processing -- loader.
        """
        dry = True
        comms_files = ['%s.%d.body' % ('email', self._id_000),
                       '%s.%d.body' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        received = self._c.process(dry=dry)
        expected = comms_files
        msg = 'Loader comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
            expected = []
            msg = 'Loader comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

    def test_process_loader_sms_error_comms(self):
        """Test processing -- SMS loader error comms.
        """
        dry = True
        comms_files = ['%s.%d.body' % ('email', self._id_000),
                       '%s.%d.body' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy mobile.
        sql = """UPDATE job_item
SET phone_nbr = '0531602145'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        received = self._c.process(dry=dry)
        expected = ['%s.%d.body' % ('email', self._id_000)]
        msg = 'Loader comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
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

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

    def test_process_loader_email_error_comms(self):
        """Test processing -- email loader error comms.
        """
        dry = True
        comms_files = ['%s.%d.body' % ('email', self._id_000),
                       '%s.%d.body' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        received = self._c.process(dry=dry)
        expected = ['%s.%d.body' % ('sms', self._id_000)]
        msg = 'Loader comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
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
                                   ('email', self._id_000, 'body'))

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

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

        received = self._c.process(dry=dry)
        expected = comms_files
        msg = 'Primary elect comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
            expected = []
            msg = 'Loader comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

    def test_process_pe_sms_error_comms(self):
        """Test processing -- SMS primary elect error comms.
        """
        dry = True
        comms_files = ['%s.%d.pe' % ('email', self._id_000),
                       '%s.%d.pe' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy mobile.
        sql = """UPDATE job_item
SET phone_nbr = '0531602145'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        received = self._c.process(dry=dry)
        expected = ['%s.%d.pe' % ('email', self._id_000)]
        msg = 'Loader comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
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

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

    def test_process_pe_email_error_comms(self):
        """Test processing -- primary elect email error comms.
        """
        dry = True
        comms_files = ['%s.%d.pe' % ('email', self._id_000),
                       '%s.%d.pe' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        received = self._c.process(dry=dry)
        expected = ['%s.%d.pe' % ('sms', self._id_000)]
        msg = 'Primary elect comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
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
                                   ('email', self._id_000, 'pe'))

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

    def test_process_pe_sms_error_comms(self):
        """Test processing -- primary elect SMS error comms.
        """
        dry = True
        comms_files = ['%s.%d.rem' % ('email', self._id_000),
                       '%s.%d.rem' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        received = self._c.process(dry=dry)
        expected = ['%s.%d.rem' % ('sms', self._id_000)]
        msg = 'Primary elect comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
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
                                   ('email', self._id_000, 'pe'))

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

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

        received = self._c.process(dry=dry)
        expected = comms_files
        msg = 'Reminder comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
            expected = []
            msg = 'Reminder comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

    def test_process_reminder_sms_error_comms(self):
        """Test processing -- SMS reminder error comms.
        """
        dry = True
        comms_files = ['%s.%d.rem' % ('email', self._id_000),
                       '%s.%d.rem' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy mobile.
        sql = """UPDATE job_item
SET phone_nbr = '0531602145'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        received = self._c.process(dry=dry)
        expected = ['%s.%d.rem' % ('email', self._id_000)]
        msg = 'Reminder comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
            expected = []
            msg = 'Reminder comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files
        else:
            files_to_delete.append('%s.%d.%s.err' %
                                   ('sms', self._id_000, 'rem'))

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

    def test_process_reminder_email_error_comms(self):
        """Test processing -- reminder email error comms.
        """
        dry = True
        comms_files = ['%s.%d.rem' % ('email', self._id_000),
                       '%s.%d.rem' % ('sms', self._id_000)]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        # Provide a dodgy email.
        sql = """UPDATE job_item
SET email_addr = '@@@tollgroup.com'
WHERE id = %d""" % self._id_000
        self._c.db(sql)

        received = self._c.process(dry=dry)
        expected = ['%s.%d.rem' % ('sms', self._id_000)]
        msg = 'Reminder comms files processed incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        if not dry:
            # Run again and no files should be processed.
            received = self._c.process(dry=dry)
            expected = []
            msg = 'Reminder comms files second pass processing incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._c.db.rollback()
        files_to_delete = dodgy
        if dry:
            files_to_delete += comms_files
        else:
            files_to_delete.append('%s.%d.%s.err' %
                                   ('email', self._id_000, 'rem'))

        for f in files_to_delete:
            os.remove(os.path.join(self._c.comms_dir, f))

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
                    'suburb': 'V031 Suburb'}
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
