import unittest2
import threading
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
        cls._file = 'nparcel/tests/files/T1250_TOLI_20130828202901.txt'
        cls._exit_event = threading.Event()
        cls._d = nparcel.LoaderDaemon(pidfile=None,
                                      config='nparcel/conf/nparceld.conf')

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
        self._d._start(self._exit_event)

        # Clean up.
        self._d.set_file(old_file)
        self._d.set_dry(old_dry)
        self._exit_event.clear()

    def test_start_non_dry_loop(self):
        """Start non-dry loop.
        """
        dry = False

        old_file = self._d.file
        old_dry = self._d.dry
        old_batch = self._d.batch
        old_in_dirs = list(self._d.config.in_dirs)
        old_archive_dir = self._d.config.archive_dir
        old_agg_dir = self._d.config.aggregator_dir
        old_support_emails = list(self._d.config.support_emails)
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
        self._d.config.set_support_emails(None)
        self._d.config.set_archive_dir(archive_dir)
        self._d.config.set_aggregator_dir(agg_dir)
        self._d._start(self._exit_event)

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
        self._d.config.set_support_emails(old_support_emails)
        self._d.config.set_aggregator_dir(old_agg_dir)
        self._d.config.cond['toli'] = old_cond
        remove_files(expected_file)
        remove_files(expected_agg_file)
        os.removedirs(in_dir)
        os.removedirs(expected_archive_dir)
        os.removedirs(agg_dir)
        self._exit_event.clear()

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
        self._d.config.set_aggregator_dir(archive_dir)

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
        self._d.config.set_aggregator_dir(old_agg_dir)

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
        self._d.config.set_aggregator_dir(agg_dir)

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
        self._d.config.set_aggregator_dir(old_agg_dir)

    @classmethod
    def tearDownClass(cls):
        del cls._file
        del cls._exit_event
        cls._d = None
        del cls._d
