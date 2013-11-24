import unittest2
import tempfile
import datetime
import os

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list,
                                 copy_file)


class TestOnDeliveryDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._odd = nparcel.OnDeliveryDaemon(pidfile=None)

        cls._report_in_dirs = tempfile.mkdtemp()
        cls._odd.set_report_in_dirs([cls._report_in_dirs])

        cls._comms_dir = tempfile.mkdtemp()
        cls._odd.set_comms_dir(cls._comms_dir)

        # Call up front to pre-load the DB.
        cls._odd.set_on_delivery(ts_db_kwargs=None)
        schema = cls._odd.od.ts_db.transsend.schema
        cls._odd.od.ts_db.create_table(name='v_nparcel_adp_connotes',
                                       schema=schema)
        fixture_file = os.path.join('nparcel',
                                    'tests',
                                    'fixtures',
                                    'transsend.py')
        cls._odd.od.ts_db.load_fixture(cls._odd.od.ts_db.transsend,
                                       fixture_file)

        cls._test_dir = 'nparcel/tests/files'
        cls._test_file = 'mts_delivery_report_20131018100758.csv'
        cls._test_filepath = os.path.join(cls._test_dir, cls._test_file)

        db = cls._odd.od.db
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
        """Intialise a OnDeliveryDaemon object.
        """
        msg = 'Not a nparcel.OnDeliveryDaemon object'
        self.assertIsInstance(self._odd, nparcel.OnDeliveryDaemon, msg)

    def test_start_dry_loop(self):
        """On Delivery _start dry loop.
        """
        old_dry = self._odd.dry

        self._odd.set_dry()
        self._odd._start(self._odd.exit_event)

        # Clean up.
        self._odd.set_dry(old_dry)
        self._odd._exit_event.clear()

    def test_start_non_dry_loop_with_transsend(self):
        """Start non-dry loop -- transsend.
        """
        dry = False

        old_dry = self._odd.dry
        old_batch = self._odd.batch
        old_support_emails = self._odd.support_emails
        old_pe_comms_ids = self._odd.pe_bu_ids
        copy_file(os.path.join(self._test_dir, self._test_file),
                  os.path.join(self._report_in_dirs, self._test_file))

        # Start processing.
        self._odd.set_dry(dry)
        self._odd.set_batch()
        self._odd.set_pe_bu_ids((1, 2, 3))
        self._odd._start(self._odd._exit_event)

        # Comms files should have been created.
        comms_files = ['email.%d.pe' % self._id_001,
                       'sms.%d.pe' % self._id_001,
                       'email.%d.pe' % self._id_004,
                       'sms.%d.pe' % self._id_004]
        expected = [os.path.join(self._comms_dir, x) for x in comms_files]
        received = get_directory_files_list(self._comms_dir)
        msg = 'On Delivery (Primary Elect) comms file error'
        self.assertListEqual(sorted(expected), sorted(received), msg)

        # Clean up.
        remove_files(expected)
        remove_files(os.path.join(self._report_in_dirs, self._test_file))
        self._odd.set_dry(old_dry)
        self._odd.set_batch(old_batch)
        self._odd.set_support_emails(old_support_emails)
        self._odd.set_pe_bu_ids(old_pe_comms_ids)
        self._odd._exit_event.clear()

    def test_start_non_dry_loop_with_transsend_no_pe_comms(self):
        """Start non-dry loop -- transsend and no PE comms IDs.
        """
        dry = False

        old_dry = self._odd.dry
        old_batch = self._odd.batch
        old_support_emails = self._odd.support_emails
        copy_file(os.path.join(self._test_dir, self._test_file),
                  os.path.join(self._report_in_dirs, self._test_file))

        # Start processing.
        self._odd.set_dry(dry)
        self._odd.set_batch()
        self._odd._start(self._odd._exit_event)

        received = get_directory_files_list(self._comms_dir)
        expected = []
        msg = 'On Delivery (Primary Elect) no PE IDs comms file error'
        self.assertListEqual(sorted(expected), sorted(received), msg)

        # Clean up.
        remove_files(os.path.join(self._report_in_dirs, self._test_file))
        self._odd.set_dry(old_dry)
        self._odd.set_batch(old_batch)
        self._odd.set_support_emails(old_support_emails)
        self._odd._exit_event.clear()

    def test_validate_file_not_mts_format(self):
        """Parse non-MTS formatted file.
        """
        f_obj = tempfile.NamedTemporaryFile()
        mts_file = f_obj.name

        received = self._odd.validate_file(mts_file)
        msg = 'Dodgy MTS file shoould not validate'
        self.assertFalse(received)

    def test_validate_file(self):
        """Parse MTS formatted file.
        """
        dir = tempfile.mkdtemp()
        f = open(os.path.join(dir,
                 'mts_delivery_report_20131018100758.csv'), 'w')
        mts_file = f.name
        f.close()

        received = self._odd.validate_file(mts_file)
        msg = 'Dodgy MTS file shoould not validate'
        self.assertTrue(received)

        # Clean up.
        remove_files(mts_file)
        os.removedirs(dir)

    def test_get_files(self):
        """Get report files.
        """
        # Seed some files.
        old_mts_files = ['mts_delivery_report_20131018100755.csv',
                         'mts_delivery_report_20131018100756.csv',
                         'mts_delivery_report_20131018100757.csv']
        mts_file = ['mts_delivery_report_20131018100758.csv']
        for file in old_mts_files + mts_file:
            fh = open(os.path.join(self._report_in_dirs, file), 'w')
            fh.close()

        received = self._odd.get_files()
        expected = [os.path.join(self._report_in_dirs, mts_file[0])]
        msg = 'MTS report files from get_files() error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        files = old_mts_files + mts_file
        remove_files([os.path.join(self._report_in_dirs, x) for x in files])

    def test_get_files_empty_report_dir(self):
        """Get report files -- empty report directory.
        """
        received = self._odd.get_files()
        expected = []
        msg = 'Report files from get_files() error'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._odd = None
        cls._test_file = None
        cls._test_filepath = None
        del cls._odd
        del cls._test_file
        del cls._test_filepath

        os.removedirs(cls._report_in_dirs)
        os.removedirs(cls._comms_dir)
        del cls._report_in_dirs
        del cls._comms_dir
