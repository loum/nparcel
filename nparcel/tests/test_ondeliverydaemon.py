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
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        # Prepare some sample data.
        # Agent.
        fixture_file = os.path.join(fixture_dir, 'agents.py')
        db.load_fixture(db.agent, fixture_file)

        cls._now = datetime.datetime.now()

        # Job table.
        fixture_file = os.path.join(fixture_dir, 'jobs.py')
        db.load_fixture(db.job, fixture_file)

        # "identity_type" table.
        fixture_file = os.path.join(fixture_dir, 'identity_type.py')
        db.load_fixture(db.identity_type, fixture_file)

        # job_items table.
        fixture_file = os.path.join(fixture_dir, 'jobitems.py')
        db.load_fixture(db.jobitem, fixture_file)

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
        received = get_directory_files_list(self._comms_dir)
        comms_files = ['email.10.pe',
                       'sms.10.pe',
                       'email.12.pe',
                       'sms.12.pe']
        expected = [os.path.join(self._comms_dir, x) for x in comms_files]
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
