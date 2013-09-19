import unittest2
import datetime

import nparcel


class TestReminder(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        # Prepare our Reminder object.
        conf = nparcel.B2CConfig()
        conf.set_config_file('nparcel/conf/nparceld.conf')
        conf.parse_config()
        proxy = conf.proxy_string()
        sms_api = conf.rest.get('sms_api')
        sms_api_username = conf.rest.get('sms_user')
        sms_api_password = conf.rest.get('sms_pw')
        sms_api_kwargs = {'api': sms_api,
                          'api_username': sms_api_username,
                          'api_password': sms_api_password}
        e_api = conf.rest.get('email_api')
        e_api_username = conf.rest.get('email_user')
        e_api_password = conf.rest.get('email_pw')
        e_api_support = conf.rest.get('failed_email')
        e_api_kwargs = {'api': e_api,
                        'api_username': e_api_username,
                        'api_password': e_api_password,
                        'support': e_api_support}

        cls._r = nparcel.Reminder(proxy=proxy,
                                  scheme='https',
                                  sms_api=sms_api_kwargs,
                                  email_api=e_api_kwargs)
        cls._r.set_template_base('nparcel')

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
        sql = cls._r.db._agent.insert_sql(agents[0])
        agent_01 = cls._r.db.insert(sql)
        sql = cls._r.db._agent.insert_sql(agents[1])
        agent_02 = cls._r.db.insert(sql)

        cls._now = datetime.datetime.now()
        jobs = [{'agent_id': agent_01,
                 'job_ts': '%s' % cls._now,
                 'bu_id': 1}]
        sql = cls._r.db.job.insert_sql(jobs[0])
        job_01 = cls._r.db.insert(sql)

        # Rules as follows:
        # id_000 - uncollected before threshold
        # id_001 - uncollected after threshold (should be found)
        # id_002 - collected after threshold
        # id_003 - uncollected after threshold, reminder already sent
        start = cls._now - datetime.timedelta(seconds=(86400 * 2))
        aged = cls._now - datetime.timedelta(seconds=(86400 * 5))
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
                     'created_ts': '%s' % aged},
                    {'connote_nbr': 'con_003',
                     'item_nbr': 'item_nbr_003',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_01,
                     'created_ts': '%s' % aged,
                     'pickup_ts': '%s' % cls._now,
                     'reminder_ts': '%s' % cls._now},
                    {'connote_nbr': 'con_004',
                     'item_nbr': 'item_nbr_004',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_01,
                     'created_ts': '%s' % aged,
                     'reminder_ts': '%s' % cls._now}]
        sql = cls._r.db.jobitem.insert_sql(jobitems[0])
        cls._id_000 = cls._r.db.insert(sql)
        sql = cls._r.db.jobitem.insert_sql(jobitems[1])
        cls._id_001 = cls._r.db.insert(sql)
        sql = cls._r.db.jobitem.insert_sql(jobitems[2])
        cls._id_002 = cls._r.db.insert(sql)
        sql = cls._r.db.jobitem.insert_sql(jobitems[3])
        cls._id_003 = cls._r.db.insert(sql)

    def test_init(self):
        """Initialise a Reminder object.
        """
        msg = 'Object is not a nparcel.Reminder'
        self.assertIsInstance(self._r, nparcel.Reminder, msg)

    def test_process(self):
        """Check processing.
        """
        dry = True
        received = self._r.process(dry=dry)
        expected = [self._id_001]
        msg = 'List of processed uncollected items incorrect'
        self.assertListEqual(received, expected, msg)

        if not dry:
            # ... and process again (no records should return)
            received = self._r.process(dry=dry)
            expected = []
            msg = 'Second pass of processed uncollected items incorrect'
            self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._r.db.rollback()

    def test_process_failed_sms(self):
        """Check processing -- failed SMS.
        """
        sql = """UPDATE job_item
SET phone_nbr = '05431602145'
WHERE id = %d""" % self._id_001
        self._r.db(sql)

        received = self._r.process(dry=True)
        expected = []
        msg = 'List of uncollected items incorrect -- failed SMS'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._r.db.rollback()

    def test_process_failed_email(self):
        """Check processing -- failed email.
        """
        sql = """UPDATE job_item
SET email_addr = '@@@.tollgroup.com'
WHERE id = %d""" % self._id_001
        self._r.db(sql)

        received = self._r.process(dry=True)
        expected = []
        msg = 'List of uncollected items incorrect -- failed email'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._r.db.rollback()

    def test_get_agent_details(self):
        """Verify agent details.
        """
        received = self._r.get_agent_details(self._id_000)
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

    def test_send_email(self):
        """Send email.
        """
        date = self._r.get_return_date(self._now)
        details = {'name': 'Mannum Newsagency',
                   'address': '77 Randwell Street',
                   'suburb': 'MANNUM',
                   'postcode': '5238',
                   'connote_nbr': 'connote_1234',
                   'item_nbr': 'item_nbr_1234',
                   'email_addr': 'loumar@tollgroup.com',
                   'date': '%s' % date}

        received = self._r.send_email(details,
                                      template='rem',
                                      dry=True)
        msg = 'Reminder email send should return True'
        self.assertTrue(received)

    def test_send_sms(self):
        """Send email.
        """
        date = self._r.get_return_date(self._now)
        details = {'name': 'Mannum Newsagency',
                   'address': '77 Randwell Street',
                   'suburb': 'MANNUM',
                   'postcode': '5238',
                   'item_nbr': 'item_nbr_1234',
                   'phone_nbr': '0431602145',
                   'date': '%s' % date}

        received = self._r.send_sms(details,
                                    template='sms_rem',
                                    dry=True)
        msg = 'Reminder SMS send should return True'
        self.assertTrue(received)

    def test_get_return_date_string_based(self):
        """Create the return date -- string based.
        """
        date_str = '2013-09-19 08:52:13.308266'
        received = self._r.get_return_date(date_str)
        expected = 'Friday 27 September 2013'
        msg = 'Generated returned date error -- string input'
        self.assertEqual(received, expected, msg)

    def test_get_return_date_none(self):
        """Create the return date -- None.
        """
        date_str = None
        received = self._r.get_return_date(date_str)
        msg = 'Generated returned date error -- None'
        self.assertIsNone(received, msg)

    def test_get_return_date_datetime_based(self):
        """Create the return date -- datetime based.
        """
        date_datetime = datetime.datetime(2013, 9, 19, 8, 52, 13, 308266)
        received = self._r.get_return_date(date_datetime)
        expected = 'Friday 27 September 2013'
        msg = 'Generated returned date error -- datetime input'
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        del cls._r
        del cls._id_000
        del cls._id_001
        del cls._id_002
        del cls._id_003
