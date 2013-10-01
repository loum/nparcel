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

        agents = [{'code': 'N031',
                   'state': 'VIC',
                   'name': 'N031 Name',
                   'address': 'N031 Address',
                   'postcode': '1234',
                   'suburb': 'N031 Suburb'},
                  {'code': 'BAD1',
                   'state': 'NSW',
                   'name': 'BAD1 Name',
                   'address': 'BAD1 Address',
                   'postcode': '5678',
                   'suburb': 'BAD1 Suburb'}]
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
        date = self._c.get_return_date(self._now)
        details = {'name': 'Primary Elect Newsagency',
                   'address': '77 Primary Street',
                   'suburb': 'ELECT',
                   'postcode': '5238',
                   'item_nbr': 'item_nbr_pe',
                   'phone_nbr': '0431602145',
                   'date': '%s' % date}

        received = self._c.send_sms(details,
                                    template='pe',
                                    dry=True)
        msg = 'Primary Elect SMS send should return True'
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
        date = self._c.get_return_date(self._now)
        details = {'name': 'PE Newsagency',
                   'address': '77 Primary Elect Street',
                   'suburb': 'Primaryville',
                   'postcode': '5238',
                   'connote_nbr': 'connote_pe',
                   'item_nbr': 'item_nbr_pe',
                   'email_addr': 'loumar@tollgroup.com',
                   'date': '%s' % date}

        received = self._c.send_email(details,
                                      template='pe',
                                      dry=True)
        msg = 'Primary elect email send should return True'
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

    def test_comms_file_missing_directory(self):
        """Get files from missing comms dir.
        """
        comms_files = ['1.rem',
                       '1111.pe',
                       '2.rem',
                       '2222.pe']
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

    def test_process(self):
        """Test processing.
        """
        #comms_files = ['%d.rem' % self._id_000,
        #               '%d.pe' % self._id_000]
        comms_files = ['%d.rem' % self._id_000]
        dodgy = ['banana',
                 'email.rem.3']
        for f in comms_files + dodgy:
            fh = open(os.path.join(self._c.comms_dir, f), 'w')
            fh.close()

        self._c.process(dry=True)

        # Cleanup.
        for f in comms_files + dodgy:
            os.remove(os.path.join(self._c.comms_dir, f))

    def test_get_agent_details(self):
        """Verify agent details.
        """
        received = self._c.get_agent_details(self._id_000)
        expected = {'address': 'N031 Address',
                    'connote_nbr': 'con_001',
                    'created_ts': '%s' % self._now,
                    'item_nbr': 'item_nbr_001',
                    'email_addr': 'loumar@tollgroup.com',
                    'phone_nbr': '0431602145',
                    'name': 'N031 Name',
                    'postcode': '1234',
                    'suburb': 'N031 Suburb'}
        msg = 'job_item.id based Agent details incorrect'
        self.assertDictEqual(received, expected, msg)

    def test_parse_comm_filename(self):
        """Verify the parse_comm_filename.
        """
        received = self._c.parse_comm_filename('')
        expected = ()
        msg = 'Filename "" incorrect'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.parse_comm_filename('333.pe')
        expected = (333, 'pe')
        msg = 'Filename "333.pe" incorrect'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.parse_comm_filename('email..pe')
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