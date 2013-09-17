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

    def test_process(self):
        """Check processing.
        """
        self._r.config.set_config_file(self._file)
        self._r.parse_config()

        # Rules as follows:
        # id_000 - uncollected before threshold
        # id_001 - uncollected after threshold (should be found)
        # id_002 - collected after threshold
        # id_003 - uncollected after threshold, reminder already sent
        now = datetime.datetime.now()
        start = now - datetime.timedelta(seconds=(86400 * 2))
        aged = now - datetime.timedelta(seconds=(86400 * 5))
        jobitems = [{'connote_nbr': 'con_001',
                     'item_nbr': 'item_nbr_001',
                     'job_id': 1,
                     'created_ts': '%s' % now},
                    {'connote_nbr': 'con_002',
                     'item_nbr': 'item_nbr_002',
                     'job_id': 2,
                     'created_ts': '%s' % aged},
                    {'connote_nbr': 'con_003',
                     'item_nbr': 'item_nbr_003',
                     'job_id': 3,
                     'created_ts': '%s' % aged,
                     'pickup_ts': '%s' % now,
                     'reminder_ts': '%s' % now},
                    {'connote_nbr': 'con_004',
                     'item_nbr': 'item_nbr_004',
                     'job_id': 4,
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

    def tearDown(self):
        self._r = None
        del self._r

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        del cls._file
