import unittest2
import datetime

import nparcel


class TestReminder(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/conf/npreminder.conf'

    def setUp(self):
        self._r = nparcel.Reminder()

    def test_init(self):
        """Initialise a Reminder object.
        """
        msg = 'Object is not a nparcel.Reminder'
        self.assertIsInstance(self._r, nparcel.Reminder, msg)

    def test_assign_missing_config(self):
        """Assign missing config file.
        """
        msg = 'Missing config file should raise error'
        self.assertRaises(SystemExit,
                          self._r.config.set_config_file, 'dodgy')

    def test_config_items(self):
        """Verify config items.
        """
        self._r.config.set_config_file(self._file)
        self._r.parse_config()

        received = self._r.notification_delay
        expected = 345600
        msg = 'Configured notification delay error'
        self.assertEqual(received, expected, msg)

        received = self._r.start_date
        expected = datetime.datetime(2013, 9, 10, 0, 0, 0)
        msg = 'Configured start date error'
        self.assertEqual(received, expected, msg)

        received = self._r.hold_period
        expected = 691200
        msg = 'Configured hold period error'
        self.assertEqual(received, expected, msg)

    def test_process(self):
        """Check processing.
        """
        self._r.config.set_config_file(self._file)
        self._r.parse_config()

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
        sql = self._r.db._agent.insert_sql(agents[0])
        agent_01 = self._r.db.insert(sql)
        sql = self._r.db._agent.insert_sql(agents[1])
        agent_02 = self._r.db.insert(sql)

        now = datetime.datetime.now()
        jobs = [{'agent_id': agent_01,
                 'job_ts': '%s' % now,
                 'bu_id': 1}]
        sql = self._r.db.job.insert_sql(jobs[0])
        job_01 = self._r.db.insert(sql)

        # Rules as follows:
        # id_000 - uncollected before threshold
        # id_001 - uncollected after threshold (should be found)
        # id_002 - collected after threshold
        # id_003 - uncollected after threshold, reminder already sent
        start = now - datetime.timedelta(seconds=(86400 * 2))
        aged = now - datetime.timedelta(seconds=(86400 * 5))
        jobitems = [{'connote_nbr': 'con_001',
                     'item_nbr': 'item_nbr_001',
                     'job_id': job_01,
                     'created_ts': '%s' % now},
                    {'connote_nbr': 'con_002',
                     'item_nbr': 'item_nbr_002',
                     'job_id': job_01,
                     'created_ts': '%s' % aged},
                    {'connote_nbr': 'con_003',
                     'item_nbr': 'item_nbr_003',
                     'job_id': job_01,
                     'created_ts': '%s' % aged,
                     'pickup_ts': '%s' % now,
                     'reminder_ts': '%s' % now},
                    {'connote_nbr': 'con_004',
                     'item_nbr': 'item_nbr_004',
                     'job_id': job_01,
                     'created_ts': '%s' % aged,
                     'reminder_ts': '%s' % now}]
        sql = self._r.db.jobitem.insert_sql(jobitems[0])
        id_000 = self._r.db.insert(sql)
        sql = self._r.db.jobitem.insert_sql(jobitems[1])
        id_001 = self._r.db.insert(sql)
        sql = self._r.db.jobitem.insert_sql(jobitems[2])
        id_002 = self._r.db.insert(sql)
        sql = self._r.db.jobitem.insert_sql(jobitems[3])
        id_003 = self._r.db.insert(sql)

        received = self._r.process()
        expected = [id_001]
        msg = 'List of processed uncollected items incorrect'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._r.db.rollback()

    def test_get_agent_details(self):
        """Verify agent details.
        """
        agent = {'code': 'N031',
                 'state': 'VIC',
                 'name': 'N031 Name',
                 'address': 'N031 Address',
                 'postcode': '1234',
                 'suburb': 'N031 Suburb'}
        sql = self._r.db._agent.insert_sql(agent)
        agent_id = self._r.db.insert(sql)

        now = datetime.datetime.now()
        job = {'agent_id': agent_id,
               'job_ts': '%s' % now,
               'bu_id': 1}
        sql = self._r.db.job.insert_sql(job)
        job_01 = self._r.db.insert(sql)

        jobitem = {'connote_nbr': 'con_001',
                   'item_nbr': 'item_nbr_001',
                   'job_id': job_01,
                   'created_ts': '%s' % now}
        sql = self._r.db.jobitem.insert_sql(jobitem)
        id_000 = self._r.db.insert(sql)

        received = self._r.get_agent_details(id_000)
        expected = {'address': 'N031 Address',
                    'connote': 'con_001',
                    'created_ts': '%s' % now,
                    'item_nbr': 'item_nbr_001',
                    'name': 'N031 Name',
                    'postcode': '1234',
                    'suburb': 'N031 Suburb'}
        msg = 'job_item.id based Agent details incorrect'
        self.assertDictEqual(received, expected, msg)

        # Cleanup.
        self._r.db.rollback()

    def tearDown(self):
        self._r = None
        del self._r

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        del cls._file
