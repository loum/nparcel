import unittest2
import threading
import tempfile
import os

import nparcel
from nparcel.utils.files import (create_dir,
                                 get_directory_files_list)


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

    def test_check_filename(self):
        """Check Nparcel filename format.
        """
        # Priority.
        received = self._d.check_filename('T1250_TOLP_20130904061851.txt')
        msg = 'Priority Nparcel filename should validate True'
        self.assertTrue(received, msg)

        # Fast.
        received = self._d.check_filename('T1250_TOLF_VIC_20130904061851.txt')
        msg = 'Fast VIC Nparcel filename should validate True'
        self.assertTrue(received, msg)

        # Dodgy.
        received = self._d.check_filename('T1250_dodgy_20130904061851.txt')
        msg = 'Dodgy Nparcel filename should validate False'
        self.assertFalse(received, msg)

    def test_start(self):
        """Start loop.
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
