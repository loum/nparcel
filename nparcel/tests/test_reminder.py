import unittest2
import datetime

import nparcel


class TestReminder(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
#        # Seed data.
#        agent = {'code': 'N031',
#                 'state': 'VIC',
#                 'name': 'N031 Name',
#                 'address': 'N031 Address',
#                 'postcode': '1234',
#                 'suburb': 'N031 Suburb'}
#        sql = self._r.db._agent.insert_sql(agent)
#        agent_id = self._r.db.insert(sql)
#
#        cls._now = datetime.datetime.now()
#        job = {'agent_id': agent_id,
#               'job_ts': '%s' % cls._now,
#               'bu_id': 1}
#        sql = self._r.db.job.insert_sql(job)
#        job_01 = self._r.db.insert(sql)
#
#        jobitem = {'connote_nbr': 'con_001',
#                   'item_nbr': 'item_nbr_001',
#                   'job_id': job_01,
#                   'created_ts': '%s' % self._now}
#        sql = self._r.db.jobitem.insert_sql(jobitem)
#        self._id_000 = self._r.db.insert(sql)

        # Prepare our Reminder object.
        conf = nparcel.B2CConfig()
        conf.set_config_file('nparcel/conf/nparceld.conf')
        conf.parse_config()
        proxy = conf.proxy_string()
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
                                  email_api=e_api_kwargs)

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
                     'job_id': job_01,
                     'created_ts': '%s' % cls._now},
                    {'connote_nbr': 'con_002',
                     'item_nbr': 'item_nbr_002',
                     'job_id': job_01,
                     'created_ts': '%s' % aged},
                    {'connote_nbr': 'con_003',
                     'item_nbr': 'item_nbr_003',
                     'job_id': job_01,
                     'created_ts': '%s' % aged,
                     'pickup_ts': '%s' % cls._now,
                     'reminder_ts': '%s' % cls._now},
                    {'connote_nbr': 'con_004',
                     'item_nbr': 'item_nbr_004',
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

        received = self._r.process()
        expected = [self._id_001]
        msg = 'List of processed uncollected items incorrect'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._r.db.rollback()

    def test_get_agent_details(self):
        """Verify agent details.
        """
        received = self._r.get_agent_details(self._id_000)
        expected = {'address': 'N031 Address',
                    'connote': 'con_001',
                    'created_ts': '%s' % self._now,
                    'item_nbr': 'item_nbr_001',
                    'name': 'N031 Name',
                    'postcode': '1234',
                    'suburb': 'N031 Suburb'}
        msg = 'job_item.id based Agent details incorrect'
        self.assertDictEqual(received, expected, msg)

    def test_send_email(self):
        """Send email.
        """
        date = self._now + datetime.timedelta(seconds=self._r.hold_period)
        details = {'name': 'Mannum Newsagency',
                   'address': '77 Randwell Street',
                   'suburb': 'MANNUM',
                   'postcode': '5238',
                   'connote': 'connote_1234',
                   'item_nbr': 'item_nbr_1234',
                   'email': 'loumar@tollgroup.com',
                   'date': '%s' % date.strftime('%Y-%m-%d')}

        received = self._r.send_email(details,
                                      base_dir='nparcel',
                                      template='rem',
                                      dry=True)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        del cls._r
        del cls._id_000
        del cls._id_001
        del cls._id_002
        del cls._id_003
