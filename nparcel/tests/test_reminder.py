import unittest2
import datetime
import tempfile
import os

import nparcel
from nparcel.utils.files import remove_files


class TestReminder(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._comms_dir = tempfile.mkdtemp()
        cls._r = nparcel.Reminder(comms_dir=cls._comms_dir)

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
                     'created_ts': '%s' % cls._now,
                     'notify_ts': '%s' % cls._now},
                    {'connote_nbr': 'con_002',
                     'item_nbr': 'item_nbr_002',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_01,
                     'created_ts': '%s' % cls._now,
                     'notify_ts': '%s' % aged},
                    {'connote_nbr': 'con_003',
                     'item_nbr': 'item_nbr_003',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_01,
                     'created_ts': '%s' % aged,
                     'notify_ts': '%s' % aged,
                     'pickup_ts': '%s' % cls._now,
                     'reminder_ts': '%s' % cls._now},
                    {'connote_nbr': 'con_004',
                     'item_nbr': 'item_nbr_004',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_01,
                     'created_ts': '%s' % cls._now,
                     'notify_ts': '%s' % aged,
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
        dry = False
        received = self._r.process(dry=dry)
        expected = [self._id_001]
        msg = 'List of processed uncollected items incorrect'
        self.assertListEqual(received, expected, msg)

        # Check that the comms files were written out.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = [os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', self._id_001, 'rem'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', self._id_001, 'rem')]
        msg = 'Comms directory file list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        remove_files(received)

    def test_process_no_recipients(self):
        """Check processing -- no recipients.
        """
        sql = """UPDATE job_item
SET phone_nbr = '', email_addr = ''
WHERE id = %d""" % self._id_001
        self._r.db(sql)
        dry = True
        received = self._r.process(dry=dry)
        expected = [self._id_001]
        msg = 'Processed uncollected items incorrect -- no recipients'

        # Cleanup.
        self._r.db.rollback()

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        del cls._r
        del cls._id_000
        del cls._id_001
        del cls._id_002
        del cls._id_003
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
