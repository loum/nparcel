import unittest2
import tempfile
import os

import nparcel
from nparcel.utils.files import (copy_file,
                                 get_directory_files_list,
                                 remove_files)


class TestFilterDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._test_dir = os.path.join('nparcel', 'tests', 'files')
        cls._file = os.path.join(cls._test_dir,
                                 'T1250_TOLI_20130828202901.txt')
        config = os.path.join('nparcel', 'conf', 'nparceld.conf')
        cls._fd = nparcel.FilterDaemon(pidfile=None, config=config)
        cls._fd.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))

    def test_init(self):
        """Initialise a FilterDaemon object.
        """
        msg = 'Not a nparcel.FilterDaemon object'
        self.assertIsInstance(self._fd, nparcel.FilterDaemon, msg)

    def test_start(self):
        """Start dry loop.
        """
        # Note: were not testing behaviour here but check that we have
        # one of each, success/error/other.
        old_file = self._fd.file
        old_dry = self._fd.dry

        self._fd.set_dry()
        self._fd.set_file(self._file)
        self._fd._start(self._fd._exit_event)

        # Clean up.
        self._fd.set_file(old_file)
        self._fd.set_dry(old_dry)
        self._fd._exit_event.clear()

    def test_start_non_dry_loop(self):
        """Start non-dry loop.
        """
        dry = False

        old_file = self._fd.file
        old_dry = self._fd.dry
        old_batch = self._fd.batch
        old_in_dirs = list(self._fd.in_dirs)
        old_support_emails = self._fd.support_emails

        in_dir = tempfile.mkdtemp()
        out_dir = tempfile.mkdtemp()
        self._fd.set_in_dirs([in_dir])
        self._fd.set_staging_base(out_dir)

        # Copy over our test files.
        t_file_dir = os.path.join('nparcel', 'tests', 'files', 'filter')
        t_files = get_directory_files_list(t_file_dir)
        for f in t_files:
            copy_file(f, os.path.join(in_dir, os.path.basename(f)))

        # Start processing.
        self._fd.set_dry(dry)
        self._fd.set_batch()
        # Add valid email address here if you want to verify support comms.
        self._fd.set_support_emails(None)
        self._fd._start(self._fd._exit_event)

        expected_out_dir = os.path.join(out_dir, 'parcelpoint', 'out')
        expected_out_filename = 'T1250_TOLP_20131118125707.txt'
        expected_out_file = os.path.join(expected_out_dir,
                                         expected_out_filename)

        # Check out directory.
        received = get_directory_files_list(expected_out_dir)
        expected = [expected_out_file]
        msg = 'Outbound directory filtered file lists do not match'
        self.assertListEqual(received, expected, msg)

        # Check contents.
        fh = open(os.path.join(self._test_dir,
                               expected_out_filename + '.filtered'))
        expected = fh.read()
        fh.close()
        fh = open(expected_out_file)
        received = fh.read()
        fh.close()
        msg = 'Filtered content error'
        self.assertEqual(expected, received, msg)

        # Clean up.
        remove_files(expected_out_file)
        os.removedirs(in_dir)
        os.removedirs(expected_out_dir)
        self._fd.set_file(old_file)
        self._fd.set_dry(old_dry)
        self._fd.set_batch(old_batch)
        self._fd.set_in_dirs(old_in_dirs)
        self._fd.set_support_emails(old_support_emails)
        self._fd._exit_event.clear()

    def test_check_filename(self):
        """Get list of inbound files.
        """
        in_dir = tempfile.mkdtemp()
        target_files = [os.path.join(in_dir, os.path.basename(self._file)),
                        os.path.join(in_dir,
                                     'T1250_TOLI_20130828202902.txt'),
                        os.path.join(in_dir,
                                     'T1250_TOLI_20130828202903.txt')]
        empty_files = [os.path.join(in_dir,
                                    'T1250_TOLI_20130828202904.txt')]
        dodgy_files = [os.path.join(in_dir, 'dodgy')]

        # Create the files.
        for f in target_files:
            copy_file(self._file, f)
        for f in empty_files + dodgy_files:
            fh = open(f, 'w')
            fh.close()

        received = self._fd.get_files([in_dir])
        expected = target_files
        msg = 'ParcelPoint directory listing not as expected'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        remove_files(target_files)
        remove_files(empty_files)
        remove_files(dodgy_files)
        os.removedirs(in_dir)

    def test_get_outbound_file(self):
        """Generate the outbound file structure.
        """
        base_dir = tempfile.mkdtemp()

        received = self._fd.get_outbound_file(self._file, dir=base_dir)
        dir = os.path.join(base_dir, 'parcelpoint', 'out')
        expected = os.path.join(dir, 'T1250_TOLI_20130828202901.txt.tmp')
        msg = 'Outbound file resource error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        os.removedirs(dir)

    def test_write(self):
        """Test outbound file write-out.
        """
        data = 'xxx'
        base_dir = tempfile.mkdtemp()

        old_staging = self._fd.staging_base
        self._fd.set_staging_base(base_dir)

        fhs = {}
        self._fd.write(data, fhs, self._file, dry=False)
        files_closed = self._fd.close(fhs)

        outfile = files_closed[0]
        fh = open(outfile)
        received = fh.read().rstrip()
        fh.close()
        expected = data + '\n%%EOF'
        msg = 'Written content error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        remove_files(outfile)
        os.removedirs(os.path.join(base_dir, 'parcelpoint', 'out'))
        self._fd.set_staging_base(old_staging)

    @classmethod
    def tearDownClass(cls):
        del cls._test_dir
        del cls._file
        cls._fd = None
        del cls._fd
