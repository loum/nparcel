import unittest2
import tempfile
import os

import top
from top.utils.files import (copy_file,
                             get_directory_files_list,
                             remove_files)


class TestFilterDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._test_dir = os.path.join('top', 'tests', 'files')
        cls._file = os.path.join(cls._test_dir,
                                 'T1250_TOLI_20130828202901.txt')
        cls._fd = top.FilterDaemon(pidfile=None)
        cls._fd.set_filters({'parcelpoint': ['P', 'R'],
                             'woolworths': ['U']})
        cls._out_dir = tempfile.mkdtemp()
        cls._fd.set_staging_base(cls._out_dir)
        cls._fd.emailer.set_template_base(os.path.join('top',
                                                       'templates'))

    def test_init(self):
        """Initialise a FilterDaemon object.
        """
        msg = 'Not a top.FilterDaemon object'
        self.assertIsInstance(self._fd, top.FilterDaemon, msg)

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
        os.removedirs(os.path.join(self._out_dir, 'parcelpoint', 'out'))
        os.removedirs(os.path.join(self._out_dir, 'woolworths', 'out'))
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
        self._fd.set_in_dirs([in_dir])

        # Copy over our test files.
        t_file_dir = os.path.join('top', 'tests', 'files', 'filter')
        t_files = get_directory_files_list(t_file_dir)
        for f in t_files:
            copy_file(f, os.path.join(in_dir, os.path.basename(f)))

        # Start processing.
        self._fd.set_dry(dry)
        self._fd.set_batch()
        # Add valid email address here if you want to verify support comms.
        self._fd.set_support_emails([])
        self._fd._start(self._fd._exit_event)

        filtered = {'parcelpoint':
                    {'dir': os.path.join(self._out_dir, 'parcelpoint', 'out'),
                     'files': ['T1250_TOLP_20131118125707.txt']},
                    'woolworths':
                    {'dir': os.path.join(self._out_dir, 'woolworths', 'out'),
                     'files': ['T1250_TOLP_20131118135041.txt',
                               'T1250_TOLP_20131118125707.txt']}}

        # Check filtered directories.
        for dp, v in filtered.iteritems():
            files = get_directory_files_list(v['dir'])
            received = [os.path.basename(x) for x in files]
            expected = v['files']
            msg = '%s filtered files error' % dp
            self.assertListEqual(sorted(received), sorted(expected), msg)

        # Check contents.
        for dp, v in filtered.iteritems():
            dir = os.path.join(self._test_dir, dp)
            for f in v['files']:
                fh = open(os.path.join(dir, f))
                expected = fh.read()
                fh.close()

                fh = open(os.path.join(v['dir'], f))
                received = fh.read()
                fh.close()
                msg = '%s %s content error' % (dp, f)
                self.assertEqual(expected, received, msg)

        # Clean up.
        for dp, v in filtered.iteritems():
            remove_files(get_directory_files_list(v['dir']))
            os.removedirs(v['dir'])
        os.removedirs(in_dir)
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

        received = self._fd.get_outbound_file('parcelpoint',
                                              self._file,
                                              dir=base_dir)
        dir = os.path.join(base_dir, 'parcelpoint', 'out')
        expected = os.path.join(dir, 'T1250_TOLI_20130828202901.txt.tmp')
        msg = 'Outbound file resource error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        os.removedirs(dir)

    def test_write(self):
        """Test outbound file write-out.
        """
        data = '%s\n' % 'xxx'

        fhs = {}
        kwargs = {'data': data,
                  'fhs': fhs,
                  'delivery_partner': 'parcelpoint',
                  'infile': self._file,
                  'dry': False}
        self._fd.write(**kwargs)
        files_closed = self._fd.close(fhs)

        outfile = files_closed[0]
        fh = open(outfile)
        received = fh.read().rstrip()
        fh.close()
        expected = data + '%%EOF'
        msg = 'Written content error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        remove_files(outfile)
        os.removedirs(os.path.join(self._out_dir, 'parcelpoint', 'out'))

    @classmethod
    def tearDownClass(cls):
        del cls._out_dir
        del cls._test_dir
        del cls._file
        del cls._fd
