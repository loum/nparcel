import unittest2
import tempfile
import os

import nparcel
from nparcel.utils.files import (create_dir,
                                 get_directory_files_list,
                                 copy_file,
                                 remove_files)


class TestLoaderDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._test_dir = os.path.join('nparcel', 'tests', 'files')
        cls._file = os.path.join(cls._test_dir,
                                 'T1250_TOLI_20130828202901.txt')
        config = os.path.join('nparcel', 'conf', 'nparceld.conf')
        cls._d = nparcel.LoaderDaemon(pidfile=None, config=config)
        cls._d.emailer.set_template_base(os.path.join('nparcel',
                                                      'templates'))
        cls._comms_dir = tempfile.mkdtemp()
        cls._d.config.set_comms_dir(cls._comms_dir)

    def test_init(self):
        """Intialise a LoaderDaemon object.
        """
        msg = 'Not a nparcel.LoaderDaemon object'
        self.assertIsInstance(self._d, nparcel.LoaderDaemon, msg)

    def test_validate_file_priority(self):
        """Validate filename -- Priority.
        """
        received = self._d.validate_file('T1250_TOLP_20130821011327.txt')
        expected = ('tolp', '2013-08-21 01:13:27')
        msg = 'Validated Priority filename parsed values incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_validate_file_fast(self):
        """Validate filename -- Fast.
        """
        received = self._d.validate_file('T1250_TOLF_VIC_20130821011327.txt')
        expected = ('tolf_vic', '2013-08-21 01:13:27')
        msg = 'Validated Fast filename parsed values incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_validate_file_ipec(self):
        """Validate filename -- Ipec.
        """
        received = self._d.validate_file('T1250_TOLI_20130821011327.txt')
        expected = ('toli', '2013-08-21 01:13:27')
        msg = 'Validated Ipec filename parsed values incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_validate_file_dodgy(self):
        """Validate filename -- dodgy.
        """
        received = self._d.validate_file('T1250_xxxx_20130821011327.txt')
        expected = (None, None)
        msg = 'Validated dodgy filename parsed values incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_start(self):
        """Start dry loop.
        """
        # Note: were not testing behaviour here but check that we have
        # one of each, success/error/other.
        old_file = self._d.file
        old_dry = self._d.dry

        self._d.set_dry()
        self._d.set_file(self._file)
        self._d._start(self._d.exit_event)

        # Clean up.
        self._d.set_file(old_file)
        self._d.set_dry(old_dry)
        self._d.exit_event.clear()

    def test_start_non_dry_loop(self):
        """Start non-dry loop.
        """
        dry = False

        old_file = self._d.file
        old_dry = self._d.dry
        old_batch = self._d.batch
        old_in_dirs = list(self._d.config.in_dirs)
        old_archive_dir = self._d.config.archive_dir
        old_agg_dir = self._d.config.aggregator_dirs
        old_support_emails = list(self._d.support_emails)
        base_dir = tempfile.mkdtemp()
        in_dir = os.path.join(base_dir, 'ipec', 'in')
        archive_dir = tempfile.mkdtemp()
        agg_dir = tempfile.mkdtemp()
        old_cond = self._d.config.cond.get('toli')
        new_cond = list(old_cond)
        new_cond[7] = '1'
        self._d.config.cond['toli'] = ''.join(new_cond)

        # Copy over our test file.
        copy_file(self._file,
                  os.path.join(in_dir, os.path.basename(self._file)))

        # Start processing.
        self._d.set_dry(dry)
        self._d.set_batch()
        self._d.config.set_in_dirs([in_dir])
        # Add valid email address here if you want to verify support comms.
        self._d.set_support_emails(None)
        self._d.config.set_archive_dir(archive_dir)
        self._d.config.set_aggregator_dirs([agg_dir])
        self._d._start(self._d.exit_event)

        # ... and make sure that the aggregator and archiver worked.
        expected_archive_dir = os.path.join(archive_dir,
                                            'ipec',
                                            '20130828')
        expected_file = os.path.join(expected_archive_dir,
                                     os.path.basename(self._file))
        expected_agg_file = os.path.join(agg_dir,
                                         os.path.basename(self._file))
        received = get_directory_files_list(expected_archive_dir)
        expected = [expected_file]
        msg = 'Non-dry process flow archive directory error'
        self.assertListEqual(received, expected, msg)

        received = get_directory_files_list(agg_dir)
        expected = [expected_agg_file]
        msg = 'Non-dry process flow aggregate directory error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._d.set_file(old_file)
        self._d.set_dry(old_dry)
        self._d.set_batch(old_batch)
        self._d.config.set_in_dirs(old_in_dirs)
        self._d.config.set_archive_dir(old_archive_dir)
        self._d.set_support_emails(old_support_emails)
        self._d.config.set_aggregator_dirs(old_agg_dir)
        self._d.config.cond['toli'] = old_cond
        remove_files(expected_file)
        remove_files(expected_agg_file)
        os.removedirs(in_dir)
        os.removedirs(expected_archive_dir)
        os.removedirs(agg_dir)
        self._d.exit_event.clear()

    def test_start_non_dry_loop_odbc_error(self):
        """Start non-dry loop to fix ODBC error when no records to commit.
        """
        dry = True

        old_file = self._d.file
        old_dry = self._d.dry
        old_batch = self._d.batch
        old_in_dirs = list(self._d.config.in_dirs)
        old_archive_dir = self._d.config.archive_dir
        old_support_emails = list(self._d.support_emails)
        # Need to connect to a MSSQL instance to reproduce this error.
        # Uncomment the following config settings to redirect to MSSQL.
        #self._d.config.set('db', 'host', '')
        #self._d.config.set('db', 'driver', 'FreeTDS')
        #self._d.config.set('db', 'database', '')
        #self._d.config.set('db', 'user', '')
        #self._d.config.set('db', 'password', '')
        #self._d.config.set('db', 'port', '1442')
        base_dir = tempfile.mkdtemp()
        in_dir = os.path.join(base_dir, 'priority', 'in')
        archive_dir = tempfile.mkdtemp()

        # Copy over our test file.
        file = 'T1250_TOLP_20131209071859.txt'
        copy_file(os.path.join(self._test_dir, file),
                  os.path.join(in_dir, os.path.basename(file)))

        # Start processing.
        self._d.set_dry(dry)
        self._d.set_batch()
        self._d.config.set_in_dirs([in_dir])
        # Add valid email address here if you want to verify support comms.
        self._d.set_support_emails(None)
        self._d.config.set_archive_dir(archive_dir)
        self._d._start(self._d.exit_event)

        # Clean up.
        self._d.set_file(old_file)
        self._d.set_dry(old_dry)
        self._d.set_batch(old_batch)
        self._d.config.set_in_dirs(old_in_dirs)
        self._d.config.set_archive_dir(old_archive_dir)
        self._d.set_support_emails(old_support_emails)
        self._d.config.remove_option('db', 'host')
        self._d.config.remove_option('db', 'driver')
        self._d.config.remove_option('db', 'database')
        self._d.config.remove_option('db', 'user')
        self._d.config.remove_option('db', 'user')
        self._d.config.remove_option('db', 'port')
        remove_files(get_directory_files_list(in_dir))
        os.removedirs(in_dir)
        os.removedirs(archive_dir)
        self._d.exit_event.clear()

    def test_start_non_dry_loop_priority(self):
        """Start non-dry loop.
        """
        dry = False

        old_dry = self._d.dry
        old_batch = self._d.batch
        old_in_dirs = list(self._d.config.in_dirs)
        old_archive_dir = self._d.config.archive_dir
        old_agg_dir = self._d.config.aggregator_dirs
        old_support_emails = list(self._d.support_emails)
        base_dir = tempfile.mkdtemp()
        in_dir = os.path.join(base_dir, 'priority', 'in')
        archive_dir = tempfile.mkdtemp()
        agg_dir = tempfile.mkdtemp()

        old_cond = self._d.config.cond.get('tolp')
        new_cond = list(old_cond)

        # Aggregate files.
        new_cond[7] = '1'

        # Send comms.
        new_cond[1] = '1'
        new_cond[2] = '1'

        # Comms Service Code flags.
        new_cond[8] = '1'
        new_cond[9] = '1'

        self._d.config.cond['tolp'] = ''.join(new_cond)

        # Copy over our test file.
        priority_file = 'nparcel/tests/files/T1250_TOLP_20130413135756.txt'
        copy_file(priority_file,
                  os.path.join(in_dir, os.path.basename(priority_file)))

        # Start processing.
        self._d.set_dry(dry)
        self._d.set_batch()
        self._d.config.set_in_dirs([in_dir])
        # Add valid email address here if you want to verify support comms.
        self._d.set_support_emails(None)
        self._d.config.set_archive_dir(archive_dir)
        self._d.config.set_aggregator_dirs([agg_dir])
        self._d._start(self._d.exit_event)

        # ... and make sure that the aggregator and archiver worked.
        expected_archive_dir = os.path.join(archive_dir,
                                            'priority',
                                            '20130413')
        expected_file = os.path.join(expected_archive_dir,
                                     os.path.basename(priority_file))
        expected_agg_file = os.path.join(agg_dir,
                                         os.path.basename(priority_file))
        received = get_directory_files_list(expected_archive_dir)
        expected = [expected_file]
        msg = 'Non-dry process flow archive directory error'
        self.assertListEqual(received, expected, msg)

        # Aggregator.
        received = get_directory_files_list(agg_dir)
        expected = [expected_agg_file]
        msg = 'Non-dry process flow aggregate directory error'
        self.assertListEqual(received, expected, msg)

        # Comms.
        comms = ['sms.1.body',
                 'email.1.body',
                 'sms.2.body',
                 'email.2.body']
        received = get_directory_files_list(self._comms_dir)
        expected_comms = [os.path.join(self._comms_dir, x) for x in comms]
        expected = expected_comms
        msg = 'Non-dry process flow comms files error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._d.set_dry(old_dry)
        self._d.set_batch(old_batch)
        self._d.config.set_in_dirs(old_in_dirs)
        self._d.config.set_archive_dir(old_archive_dir)
        self._d.set_support_emails(old_support_emails)
        self._d.config.set_aggregator_dirs(old_agg_dir)
        self._d.config.cond['tolp'] = old_cond
        remove_files(expected_file)
        remove_files(expected_agg_file)
        remove_files(expected_comms)
        os.removedirs(in_dir)
        os.removedirs(expected_archive_dir)
        os.removedirs(agg_dir)
        self._d.exit_event.clear()

    def test_start_non_dry_loop_priority_sc_1_no_aggregator(self):
        """Start non-dry loop.
        """
        dry = False

        old_dry = self._d.dry
        old_batch = self._d.batch
        old_in_dirs = list(self._d.config.in_dirs)
        old_archive_dir = self._d.config.archive_dir
        old_agg_dir = self._d.config.aggregator_dirs
        old_support_emails = list(self._d.support_emails)
        base_dir = tempfile.mkdtemp()
        in_dir = os.path.join(base_dir, 'priority', 'in')
        archive_dir = tempfile.mkdtemp()
        agg_dir = tempfile.mkdtemp()

        old_cond = self._d.config.cond.get('tolp')
        new_cond = list(old_cond)

        # Send comms.
        new_cond[1] = '1'
        new_cond[2] = '1'

        # Comms Service Code flags.
        new_cond[8] = '1'

        self._d.config.cond['tolp'] = ''.join(new_cond)

        # Copy over our test file.
        priority_file = 'nparcel/tests/files/T1250_TOLP_20130413135756.txt'
        copy_file(priority_file,
                  os.path.join(in_dir, os.path.basename(priority_file)))

        # Start processing.
        self._d.set_dry(dry)
        self._d.set_batch()
        self._d.config.set_in_dirs([in_dir])
        # Add valid email address here if you want to verify support comms.
        self._d.set_support_emails(None)
        self._d.config.set_archive_dir(archive_dir)
        self._d.config.set_aggregator_dirs([agg_dir])
        self._d._start(self._d.exit_event)

        # ... and make sure that the aggregator and archiver worked.
        expected_archive_dir = os.path.join(archive_dir,
                                            'priority',
                                            '20130413')
        expected_file = os.path.join(expected_archive_dir,
                                     os.path.basename(priority_file))
        expected_agg_file = os.path.join(agg_dir,
                                         os.path.basename(priority_file))
        received = get_directory_files_list(expected_archive_dir)
        expected = [expected_file]
        msg = 'Non-dry process flow archive directory error'
        self.assertListEqual(received, expected, msg)

        # Aggregator.
        received = get_directory_files_list(agg_dir)
        expected = []
        msg = 'Non-dry process flow aggregate directory error'
        self.assertListEqual(received, expected, msg)

        # Comms.
        comms = ['sms.1.body',
                 'email.1.body']
        received = get_directory_files_list(self._comms_dir)
        expected_comms = [os.path.join(self._comms_dir, x) for x in comms]
        expected = expected_comms
        msg = 'Non-dry process flow comms files error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._d.set_dry(old_dry)
        self._d.set_batch(old_batch)
        self._d.config.set_in_dirs(old_in_dirs)
        self._d.config.set_archive_dir(old_archive_dir)
        self._d.set_support_emails(old_support_emails)
        self._d.config.set_aggregator_dirs(old_agg_dir)
        self._d.config.cond['tolp'] = old_cond
        remove_files(expected_file)
        remove_files(expected_comms)
        os.removedirs(in_dir)
        os.removedirs(expected_archive_dir)
        os.removedirs(agg_dir)
        self._d.exit_event.clear()

    def test_start_non_dry_loop_priority_sc_2_aggregator(self):
        """Start non-dry loop.
        """
        dry = False

        old_dry = self._d.dry
        old_batch = self._d.batch
        old_in_dirs = list(self._d.config.in_dirs)
        old_archive_dir = self._d.config.archive_dir
        old_agg_dir = self._d.config.aggregator_dirs
        old_support_emails = list(self._d.support_emails)
        base_dir = tempfile.mkdtemp()
        in_dir = os.path.join(base_dir, 'priority', 'in')
        archive_dir = tempfile.mkdtemp()
        agg_dir = tempfile.mkdtemp()

        old_cond = self._d.config.cond.get('tolp')
        new_cond = list(old_cond)

        # Aggregate files.
        new_cond[7] = '1'

        # Send comms.
        new_cond[1] = '1'
        new_cond[2] = '1'

        # Comms Service Code flags.
        new_cond[9] = '1'

        self._d.config.cond['tolp'] = ''.join(new_cond)

        # Copy over our test file.
        priority_file = 'nparcel/tests/files/T1250_TOLP_20130413135756.txt'
        copy_file(priority_file,
                  os.path.join(in_dir, os.path.basename(priority_file)))

        # Start processing.
        self._d.set_dry(dry)
        self._d.set_batch()
        self._d.config.set_in_dirs([in_dir])
        # Add valid email address here if you want to verify support comms.
        self._d.set_support_emails(None)
        self._d.config.set_archive_dir(archive_dir)
        self._d.config.set_aggregator_dirs([agg_dir])
        self._d._start(self._d.exit_event)

        # ... and make sure that the aggregator and archiver worked.
        expected_archive_dir = os.path.join(archive_dir,
                                            'priority',
                                            '20130413')
        expected_file = os.path.join(expected_archive_dir,
                                     os.path.basename(priority_file))
        expected_agg_file = os.path.join(agg_dir,
                                         os.path.basename(priority_file))
        received = get_directory_files_list(expected_archive_dir)
        expected = [expected_file]
        msg = 'Non-dry process flow archive directory error'
        self.assertListEqual(received, expected, msg)

        # Aggregator.
        received = get_directory_files_list(agg_dir)
        expected = [expected_agg_file]
        msg = 'Non-dry process flow aggregate directory error'
        self.assertListEqual(received, expected, msg)

        # Comms.
        comms = ['sms.2.body',
                 'email.2.body']
        received = get_directory_files_list(self._comms_dir)
        expected_comms = [os.path.join(self._comms_dir, x) for x in comms]
        expected = expected_comms
        msg = 'Non-dry process flow comms files error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._d.set_dry(old_dry)
        self._d.set_batch(old_batch)
        self._d.config.set_in_dirs(old_in_dirs)
        self._d.config.set_archive_dir(old_archive_dir)
        self._d.set_support_emails(old_support_emails)
        self._d.config.set_aggregator_dirs(old_agg_dir)
        self._d.config.cond['tolp'] = old_cond
        remove_files(expected_file)
        remove_files(expected_agg_file)
        remove_files(expected_comms)
        os.removedirs(in_dir)
        os.removedirs(expected_archive_dir)
        os.removedirs(agg_dir)
        self._d.exit_event.clear()

    def test_start_non_dry_loop_priority_sc_4_delayed(self):
        """Start non-dry loop Service Code 4 delayed template.
        """
        dry = False

        old_dry = self._d.dry
        old_batch = self._d.batch
        old_in_dirs = list(self._d.config.in_dirs)
        old_archive_dir = self._d.config.archive_dir
        old_agg_dir = self._d.config.aggregator_dirs
        old_support_emails = list(self._d.support_emails)
        base_dir = tempfile.mkdtemp()
        in_dir = os.path.join(base_dir, 'priority', 'in')
        archive_dir = tempfile.mkdtemp()
        agg_dir = tempfile.mkdtemp()

        old_cond = self._d.config.cond.get('tolp')
        new_cond = list(old_cond)

        # Send comms.
        new_cond[1] = '1'
        new_cond[2] = '1'

        # Comms Service Code 4 send flag.
        new_cond[10] = '1'

        # Delayed template.
        new_cond[11] = '1'

        self._d.config.cond['tolp'] = ''.join(new_cond)

        # Copy over our test file.
        priority_file = 'nparcel/tests/files/T1250_TOLP_20130413135756.txt'
        copy_file(priority_file,
                  os.path.join(in_dir, os.path.basename(priority_file)))

        # Start processing.
        self._d.set_dry(dry)
        self._d.set_batch()
        self._d.config.set_in_dirs([in_dir])
        # Add valid email address here if you want to verify support comms.
        self._d.set_support_emails(None)
        self._d.config.set_archive_dir(archive_dir)
        self._d.config.set_aggregator_dirs([agg_dir])
        self._d._start(self._d.exit_event)

        # ... and make sure that the aggregator and archiver worked.
        expected_archive_dir = os.path.join(archive_dir,
                                            'priority',
                                            '20130413')
        expected_file = os.path.join(expected_archive_dir,
                                     os.path.basename(priority_file))
        expected_agg_file = os.path.join(agg_dir,
                                         os.path.basename(priority_file))
        received = get_directory_files_list(expected_archive_dir)
        expected = [expected_file]
        msg = 'Non-dry process flow archive directory error'
        self.assertListEqual(received, expected, msg)

        # Comms.
        comms = ['sms.3.delay',
                 'email.3.delay']
        received = get_directory_files_list(self._comms_dir)
        expected_comms = [os.path.join(self._comms_dir, x) for x in comms]
        expected = expected_comms
        msg = 'Non-dry process flow comms files error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._d.set_dry(old_dry)
        self._d.set_batch(old_batch)
        self._d.config.set_in_dirs(old_in_dirs)
        self._d.config.set_archive_dir(old_archive_dir)
        self._d.set_support_emails(old_support_emails)
        self._d.config.set_aggregator_dirs(old_agg_dir)
        self._d.config.cond['tolp'] = old_cond
        remove_files(expected_file)
        remove_files(expected_agg_file)
        remove_files(expected_comms)
        os.removedirs(in_dir)
        os.removedirs(expected_archive_dir)
        os.removedirs(agg_dir)
        self._d.exit_event.clear()

    def test_distribute_file(self):
        """Distribute the T1250 file.
        """
        base_dir = tempfile.mkdtemp()
        source_dir = os.path.join(base_dir, 'ipec', 'in')
        create_dir(source_dir)
        archive_dir = tempfile.mkdtemp()
        agg_dir = tempfile.mkdtemp()
        old_archive_dir = self._d.config.archive_dir
        self._d.config.set_archive_dir(archive_dir)
        old_agg_dir = self._d.config.archive_dir
        self._d.config.set_aggregator_dirs([archive_dir])

        # Fudge a T1250.
        test_file = 'T1250_TOLI_20130828202901.txt'
        fh = open(os.path.join(source_dir, test_file), 'w')
        fh.close()

        expected_archive_dir = os.path.join(archive_dir,
                                           'ipec',
                                           '20130828')

        # Test the archive.
        self._d.distribute_file(os.path.join(source_dir, test_file))
        received = get_directory_files_list(expected_archive_dir)
        expected = [os.path.join(expected_archive_dir, test_file)]
        msg = 'Archived file error'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        os.remove(os.path.join(expected_archive_dir, test_file))
        os.removedirs(source_dir)
        os.removedirs(expected_archive_dir)
        os.removedirs(agg_dir)
        self._d.config.set_archive_dir(old_archive_dir)
        self._d.config.set_aggregator_dirs(old_agg_dir)

    def test_distribute_file_with_aggregator_set(self):
        """Distribute the T1250 file.
        """
        base_dir = tempfile.mkdtemp()
        source_dir = os.path.join(base_dir, 'ipec', 'in')
        create_dir(source_dir)
        archive_dir = tempfile.mkdtemp()
        agg_dir = tempfile.mkdtemp()
        old_archive_dir = self._d.config.archive_dir
        self._d.config.set_archive_dir(archive_dir)
        old_agg_dir = self._d.config.archive_dir
        self._d.config.set_aggregator_dirs([agg_dir])

        # Fudge a T1250.
        test_file = 'T1250_TOLI_20130828202901.txt'
        fh = open(os.path.join(source_dir, test_file), 'w')
        fh.close()

        self._d.distribute_file(os.path.join(source_dir, test_file),
                                aggregate_file=True)

        # Test the archive.
        expected_archive_dir = os.path.join(archive_dir,
                                           'ipec',
                                           '20130828')
        received = get_directory_files_list(expected_archive_dir)
        expected = [os.path.join(expected_archive_dir, test_file)]
        msg = 'Archived file error'
        self.assertListEqual(received, expected, msg)

        # Test the aggregator directory.
        received = get_directory_files_list(agg_dir)
        expected = [os.path.join(agg_dir, test_file)]
        msg = 'Aggregate file error'

        # Cleanup.
        os.remove(os.path.join(expected_archive_dir, test_file))
        os.remove(os.path.join(agg_dir, test_file))
        os.removedirs(source_dir)
        os.removedirs(expected_archive_dir)
        os.removedirs(agg_dir)
        self._d.config.set_archive_dir(old_archive_dir)
        self._d.config.set_aggregator_dirs(old_agg_dir)

    def test_get_comms_delivery_partners(self):
        """Verify the comms delivery partners per BU.
        """
        old_dps = self._d.comms_delivery_partners

        dps = {'priority': ['Nparcel'],
               'fast': ['Nparcel', 'ParcelPoint'],
               'ipec': ['Nparcel', 'ParcelPoint', 'Toll']}
        self._d.set_comms_delivery_partners(dps)

        bu_id = 1
        received = self._d.get_comms_delivery_partners(bu_id)
        expected = ['Nparcel']
        msg = 'bu_id 1 -- Delivery Partner list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        bu_id = 2
        received = self._d.get_comms_delivery_partners(bu_id)
        expected = ['Nparcel', 'ParcelPoint']
        msg = 'bu_id 2 -- Delivery Partner list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        bu_id = 3
        received = self._d.get_comms_delivery_partners(bu_id)
        expected = ['Nparcel', 'ParcelPoint', 'Toll']
        msg = 'bu_id 3 -- Delivery Partner list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        bu_id = 4
        received = self._d.get_comms_delivery_partners(bu_id)
        expected = []
        msg = 'bu_id 4 -- Delivery Partner list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._d.set_comms_delivery_partners(old_dps)

    @classmethod
    def tearDownClass(cls):
        del cls._test_dir
        del cls._file
        cls._d = None
        del cls._d
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
