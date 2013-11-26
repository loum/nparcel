import unittest2
import datetime
import tempfile
import os

import nparcel
from nparcel.utils.files import remove_files


class TestOnDelivery(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._comms_dir = tempfile.mkdtemp()
        cls._on = nparcel.OnDelivery(comms_dir=cls._comms_dir)
        cls._on.ts_db.create_table(name='v_nparcel_adp_connotes',
                                   schema=cls._on.ts_db.transsend.schema)
        fixture_file = os.path.join('nparcel',
                                    'tests',
                                    'fixtures',
                                    'transsend.py')
        cls._on.ts_db.load_fixture(cls._on.ts_db.transsend, fixture_file)

        test_dir = 'nparcel/tests/files'
        test_file = 'mts_delivery_report_20131018100758.csv'
        cls._test_file = os.path.join(test_dir, test_file)

        db = cls._on.db
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
        sql = db._agent.insert_sql(agents[0])
        agent_01 = db.insert(sql)
        sql = db._agent.insert_sql(agents[1])
        agent_02 = db.insert(sql)

        cls._now = datetime.datetime.now()
        jobs = [{'agent_id': agent_01,
                 'job_ts': '%s' % cls._now,
                 'bu_id': 1},
                {'agent_id': agent_01,
                 'job_ts': '%s' % cls._now,
                 'service_code': 3,
                 'bu_id': 1},
                {'agent_id': agent_01,
                 'job_ts': '%s' % cls._now,
                 'service_code': 3,
                 'bu_id': 2}]
        sql = db.job.insert_sql(jobs[0])
        job_01 = db.insert(sql)
        sql = db.job.insert_sql(jobs[1])
        job_02 = db.insert(sql)
        sql = db.job.insert_sql(jobs[2])
        job_03 = db.insert(sql)

        # Rules as follows:
        # id_000 - not primary elect
        # id_001 - primary elect with valid recipients/delivered
        # id_002 - primary elect no recipients
        # id_003 - primary elect/not delivered
        # id_004 - primary elect/delivered (TransSend)
        # id_005 - primary elect/not delivered (TransSend)
        jobitems = [{'connote_nbr': 'con_001',
                     'item_nbr': 'item_nbr_001',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_01,
                     'created_ts': '%s' % cls._now},
                    {'connote_nbr': 'GOLW010997',
                     'item_nbr': 'item_nbr_002',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_02,
                     'created_ts': '%s' % cls._now},
                    {'connote_nbr': 'con_003',
                     'item_nbr': 'item_nbr_003',
                     'email_addr': '',
                     'phone_nbr': '',
                     'job_id': job_02,
                     'created_ts': '%s' % cls._now,
                     'pickup_ts': '%s' % cls._now},
                    {'connote_nbr': 'GOLW013730',
                     'item_nbr': 'item_nbr_004',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_02,
                     'created_ts': '%s' % cls._now},
                    {'connote_nbr': 'ANWD011307',
                     'item_nbr': 'ANWD011307001',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_03,
                     'created_ts': '%s' % cls._now},
                    {'connote_nbr': 'IANZ012764',
                     'item_nbr': 'IANZ012764',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145',
                     'job_id': job_03,
                     'created_ts': '%s' % cls._now}]
        sql = db.jobitem.insert_sql(jobitems[0])
        cls._id_000 = db.insert(sql)
        sql = db.jobitem.insert_sql(jobitems[1])
        cls._id_001 = db.insert(sql)
        sql = db.jobitem.insert_sql(jobitems[2])
        cls._id_002 = db.insert(sql)
        sql = db.jobitem.insert_sql(jobitems[3])
        cls._id_003 = db.insert(sql)
        sql = db.jobitem.insert_sql(jobitems[4])
        cls._id_004 = db.insert(sql)
        sql = db.jobitem.insert_sql(jobitems[5])
        cls._id_005 = db.insert(sql)
        db.commit()

    def test_init(self):
        """Initialise a OnDelivery object.
        """
        msg = 'Object is not a nparcel.OnDelivery'
        self.assertIsInstance(self._on, nparcel.OnDelivery, msg)

    def test_get_primary_elect_job_item_id_not_pe(self):
        """jobitem.id's of connote that is not a primary elect job.
        """
        received = self._on.get_primary_elect_job_item_id('con_001')
        expected = []
        msg = 'Non-primary elect job should produce empty list'
        self.assertListEqual(received, expected, msg)

    def test_get_primary_elect_job_item_id_valid_pe(self):
        """jobitem.id's of connote that is a primary elect job.
        """
        received = self._on.get_primary_elect_job_item_id('GOLW010997')
        expected = [self._id_001]
        msg = 'Primary elect job should produce ids'
        self.assertListEqual(received, expected, msg)

    def test_get_primary_elect_job_item_id_valid_pe_no_comms(self):
        """jobitem.id's of connote that is a primary elect job -- no comms.
        """
        received = self._on.get_primary_elect_job_item_id('con_003')
        expected = []
        msg = 'Primary elect job no recipients should produce empty list'
        self.assertListEqual(received, expected, msg)

    def test_process_dry_run(self):
        """Check processing -- dry run.
        """
        dry = True

        service_code = 3
        bu_ids = (1, 2, 3)
        received = self._on.process(template='pe',
                                    service_code=service_code,
                                    bu_ids=bu_ids,
                                    mts_file=self._test_file,
                                    dry=dry)
        expected = []
        msg = 'List of processed primary elect items incorrect'
        self.assertListEqual(received, expected, msg)

    def test_process(self):
        """Check processing.
        """
        dry = False

        service_code = 3
        bu_ids = (1, 2, 3)
        received = self._on.process(template='pe',
                                    service_code=service_code,
                                    bu_ids=bu_ids,
                                    mts_file=self._test_file,
                                    dry=dry)
        expected = [self._id_001, self._id_004]
        msg = 'List of processed primary elect items incorrect'
        self.assertListEqual(received, expected, msg)

        # Check that the comms files were written out.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = [os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', self._id_001, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', self._id_001, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', self._id_004, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', self._id_004, 'pe')]
        msg = 'Comms directory file list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        remove_files(received)

    def test_process_inline(self):
        """Check processing.
        """
        dry = False

        template = 'pe'
        service_code = 3
        bu_ids = (1, 2, 3)
        job_items = [(5, 'ANWD011307', 'ANWD011307001')]

        received = self._on.process(template=template,
                                    service_code=service_code,
                                    bu_ids=bu_ids,
                                    job_items=job_items,
                                    mts_file=self._test_file,
                                    dry=dry)
        expected = [self._id_004]
        msg = 'List of processed primary elect items incorrect'
        self.assertListEqual(received, expected, msg)

        # Check that the comms files were written out.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = [os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', self._id_004, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', self._id_004, 'pe')]
        msg = 'Comms directory file list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        remove_files(received)

    def test_process_no_mts_file(self):
        """Check processing -- no MTS file.
        """
        dry = False

        template = 'pe'
        service_code = 3
        bu_ids = (1, 2, 3)
        received = self._on.process(template=template,
                                    service_code=service_code,
                                    bu_ids=bu_ids,
                                    dry=dry)
        expected = [self._id_004]
        msg = 'Processed primary elect should return empty list'
        self.assertListEqual(received, expected, msg)

        # Check that the comms files were written out.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = [os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', self._id_004, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', self._id_004, 'pe')]
        msg = 'Comms directory file list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        remove_files(received)

    def test_connote_delivered_no_db(self):
        """Query delivered status against TransSend.
        """
        connote = 'APLD029228'
        item_nbr = 'APLD029228001'

        received = self._on.connote_delivered(connote, item_nbr)
        msg = 'TransSend delivery check should be False -- no DB conn'
        self.assertFalse(received)

    def test_connote_delivered_not_delivered(self):
        """Query delivered status against TransSend -- not delivered.
        """
        connote = 'APLD029228'
        item_nbr = 'APLD029228001'

        received = self._on.connote_delivered(connote, item_nbr)
        msg = 'TransSend delivery check should be False'
        self.assertFalse(received)

    def test_connote_delivered_delivered(self):
        """Query delivered status against TransSend -- delivered.
        """
        connote = 'ANWD011307'
        item_nbr = 'ANWD011307001'

        received = self._on.connote_delivered(connote, item_nbr)
        msg = 'TransSend delivery check should be True'
        self.assertTrue(received)

    @classmethod
    def tearDownClass(cls):
        cls._on = None
        del cls._on
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
        del cls._test_file
