import unittest2
import os
import re
import tempfile

import nparcel
from nparcel.utils.files import (check_eof_flag,
                                 remove_files,
                                 get_directory_files_list,
                                 copy_file)


class TestMapperDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        dir = os.path.join('nparcel', 'tests', 'files')
        cls._file = os.path.join(dir, 'T1250_TOLI_20131011115618.dat')
        cls._md = nparcel.MapperDaemon(pidfile=None)

        cls._md.set_in_dirs([dir])
        cls._archive_base = tempfile.mkdtemp()
        cls._md.set_archive_base(cls._archive_base)

    def test_init(self):
        """Intialise a MapperDaemon object.
        """
        msg = 'Not a nparcel.MapperDaemon object'
        self.assertIsInstance(self._md, nparcel.MapperDaemon, msg)

    def test_start(self):
        """MapperDaemon _start processing loop.
        """
        # Note: were not testing behaviour here but check that we have
        # one of each, success/error/other.
        old_file = self._md.file
        old_dry = self._md.dry

        self._md.set_dry()
        self._md._start(self._md.exit_event)

        # Clean up.
        self._md.set_file(old_file)
        self._md.set_dry(old_dry)
        self._md.exit_event.clear()

    def test_start_non_dry(self):
        """Start non-dry loop.
        """
        dry = False

        old_file = self._md.file
        old_dry = self._md.dry
        old_batch = self._md.batch
        old_support_emails = list(self._md.support_emails)
        old_in_dirs = self._md.in_dirs

        # Prepare test environment.
        self._md.set_dry(dry)
        self._md.set_batch(True)
        in_dir = tempfile.mkdtemp()
        self._md.set_in_dirs([in_dir])
        copy_file(self._file, os.path.join(in_dir,
                                           os.path.basename(self._file)))

        # Start processing.
        self._md._start(self._md.exit_event)
        # Add valid email address here if you want to verify support comms.
        self._md.set_support_emails(None)

        expected_archive_dir = os.path.join(self._archive_base,
                                            'gis',
                                            '20131011')
        expected_file = get_directory_files_list(in_dir)

        # Clean up.
        self._md.set_file(old_file)
        self._md.set_dry(old_dry)
        self._md.set_batch(old_batch)
        self._md.set_support_emails(old_support_emails)
        self._md.set_in_dirs(old_in_dirs)
        remove_files(expected_file)
        remove_files(os.path.join(expected_archive_dir,
                                  os.path.basename(self._file)))
        os.removedirs(in_dir)
        os.removedirs(expected_archive_dir)
        self._md.exit_event.clear()

    def test_start_provide_file(self):
        """Drive the _start() method with a file.
        """
        self._md.set_file(self._file)

        self._md.set_dry()
        self._md._start(self._md.exit_event)

        # Clean up.
        self._md.set_file()

    def test_start_provide_directory(self):
        """Drive the _start() method with a directory.
        """
        self._md.set_dry()
        self._md._start(self._md.exit_event)

    def test_get_customer_archive(self):
        """Extract GIS T1250 timestamp.
        """
        received = self._md.get_customer_archive(self._file)
        expected = os.path.join(self._md.archive_base,
                                self._md.customer,
                                '20131011',
                                os.path.basename(self._file))
        msg = 'GIS T1250 archive directory error'
        self.assertEqual(received, expected, msg)

    def test_get_files(self):
        """Get GIS files.
        """
        dir = tempfile.mkdtemp()

        # Create some files.
        ok_files = ['T1250_TOLP_20131011115618.dat',
                    'T1250_TOLF_20131011115619.dat',
                    'T1250_TOLI_20131011115620.dat']
        dodge_files = ['dodgy']
        for file in ok_files + dodge_files:
            fh = open(os.path.join(dir, file), 'w')
            fh.write('%%EOF\r\n')
            fh.close()

        received = self._md.get_files(dir=[dir])
        expected = [os.path.join(dir, x) for x in ok_files]
        msg = 'GIS files to process not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        remove_files([os.path.join(dir, x) for x in ok_files + dodge_files])
        os.removedirs(dir)

    def test_get_files_with_archive(self):
        """Get GIS files with an archived file.
        """
        dir = tempfile.mkdtemp()
        archive_dir = os.path.join(self._archive_base,
                                   'gis',
                                   '20131011')
        os.makedirs(archive_dir)

        # Create some files.
        ok_files = ['T1250_TOLP_20131011115618.dat',
                    'T1250_TOLI_20131011115619.dat',
                    'T1250_TOLI_20131011115620.dat']
        dodge_files = ['dodgy']

        for file in ok_files + dodge_files:
            fh = open(os.path.join(dir, file), 'w')
            fh.write('%%EOF\r\n')
            fh.close()

        archived_files = ['T1250_TOLI_20131011115619.dat']
        for file in archived_files:
            fh = open(os.path.join(archive_dir, file), 'w')
            fh.write('%%EOF\r\n')
            fh.close()

        received = self._md.get_files(dir=[dir])
        expected_files = [x for x in ok_files if x not in archived_files]
        expected = [os.path.join(dir, y) for y in expected_files]
        msg = 'GIS files to process not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        files = ok_files + dodge_files
        remove_files([os.path.join(dir, x) for x in files])
        remove_files([os.path.join(archive_dir, x) for x in archived_files])

        os.removedirs(dir)
        os.removedirs(archive_dir)

    def test_write_new_file_handle(self):
        """Write out T1250 file to new file handle.
        """
        dir = tempfile.mkdtemp()

        dry = False
        data = ('TOLP', 'data string')
        fhs = {}
        received = self._md.write(data, fhs, dir=dir, dry=dry)
        msg = 'T1250 write-out to new file handle should return True'
        self.assertTrue(received, msg)

        # Close file handles.
        files = []
        for fh in fhs.values():
            files.append(fh.name)
            fh.close()

        received = len(files)
        expected = 1
        msg = 'T1250 write-out should only produce 1 file'
        self.assertEqual(received, expected, msg)

        fh = open(files[0])
        received = fh.read().rstrip()
        expected = 'data string'
        msg = 'T1250 file content incorrect'
        self.assertEqual(received, expected, msg)

        # Clean up.
        remove_files([fhs[x].name for x in fhs.keys()])
        os.removedirs(dir)

    def test_write_no_data(self):
        """Write out T1250 file no data.
        """
        dry = True
        data = ()
        fhs = {}
        received = self._md.write(data, fhs, dry=dry)
        msg = 'T1250 write-out with no data should return False'
        self.assertFalse(received, msg)

    def test_close(self):
        """Close out T1250 file.
        """
        dir = tempfile.mkdtemp()
        file = 'T1250_TOLP_20131014110400.txt.tmp'
        filepath = os.path.join(dir, file)

        fhs = {}
        fhs['TOLP'] = open(filepath, 'w')
        received = self._md.close(fhs)
        expected = [re.sub('\.tmp$', '', filepath)]
        msg = 'List of closed T1250 incorrect'
        self.assertListEqual(received, expected, msg)

        # Check that they are valid T1250 files.
        msg = 'Closed file is not a valid T1250'
        for file in expected:
            self.assertTrue(check_eof_flag(file), msg)

        # Clean up.
        remove_files(expected)
        os.removedirs(dir)

    def test_close_no_open_file_handles(self):
        """Attempt to close out file when no file handles are presented.
        """
        fhs = {}
        received = self._md.close(fhs)
        expected = []
        msg = 'Closed file list against empty file handle list incorrect'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        del cls._file
        cls._md = None
        del cls._md
        try:
            os.removedirs(cls._archive_base)
        except OSError:
            pass
        del cls._archive_base
