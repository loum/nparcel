import unittest2
import os
import tempfile

import nparcel


class TestMapperDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._md = nparcel.MapperDaemon(pidfile=None,
                                       config='nparcel/conf/nparceld.conf')
        dir = 'nparcel/tests/files'
        cls._md.config.set_pe_in_dirs([dir])

    def test_init(self):
        """Intialise a MapperDaemon object.
        """
        msg = 'Not a nparcel.MapperDaemon object'
        self.assertIsInstance(self._md, nparcel.MapperDaemon, msg)

    def test_start(self):
        """MapperDaemon _start processing loop.
        """
        self._md.set_dry()
        self._md._start(self._md.exit_event)

    def test_start_provide_file(self):
        """Drive the _start() method with a file.
        """
        f = 'nparcel/tests/files/T1250_TOLI_20131011115618.dat'
        self._md.set_file(f)

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
        archive_dir = tempfile.mkdtemp()
        old_archive_dir = self._md.config.archive_dir
        self._md.config.set_archive_dir(archive_dir)

        f = 'nparcel/tests/files/T1250_TOLI_20131011115618.dat'
        received = self._md.get_customer_archive(f)
        expected = os.path.join(self._md.config.archive_dir,
                                self._md.config.pe_customer,
                                '20131011',
                                os.path.basename(f))
        msg = 'GIS T1250 archive directory error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._md.set_file()
        os.removedirs(archive_dir)
        self._md.config.set_archive_dir(old_archive_dir)

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

        received = self._md.get_files(dir=dir)
        expected = [os.path.join(dir, x) for x in ok_files]
        msg = 'GIS files to process not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        for file in ok_files + dodge_files:
            os.remove(os.path.join(dir, file))

        os.removedirs(dir)

    def test_get_files_with_archive(self):
        """Get GIS files with an archived file.
        """
        dir = tempfile.mkdtemp()
        old_archive_dir = self._md.config.archive_dir
        archive_dir_base = tempfile.mkdtemp()
        self._md.config.set_archive_dir(archive_dir_base)
        archive_dir = os.path.join(archive_dir_base, 'gis', '20131011')
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

        received = self._md.get_files(dir=dir)
        expected_files = [x for x in ok_files if x not in archived_files]
        expected = [os.path.join(dir, y) for y in expected_files]
        msg = 'GIS files to process not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        for file in ok_files + dodge_files:
            os.remove(os.path.join(dir, file))
        for file in archived_files:
            os.remove(os.path.join(archive_dir, file))

        os.removedirs(dir)
        os.removedirs(archive_dir)

        self._md.config.set_archive_dir(old_archive_dir)

    @classmethod
    def tearDownClass(cls):
        cls._md = None
        del cls._md
