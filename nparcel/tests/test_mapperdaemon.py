import unittest2
import os
import tempfile

import nparcel


class TestMapperDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._md = nparcel.MapperDaemon(pidfile=None,
                                       config='nparcel/conf/nparceld.conf')

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
        old_dirs = self._md.config.pe_in_dirs
        dir = 'nparcel/tests/files'
        self._md.config.set_pe_in_dirs([dir])

        self._md.set_dry()
        self._md._start(self._md.exit_event)

        # Clean up.
        self._md.config.set_pe_in_dirs(old_dirs)

    def test_get_files(self):
        """Get GIS files.
        """
        dir = tempfile.mkdtemp()

        # Create some files.
        ok_files = ['T1250_TOLP_20131011115618.dat',
                    'T1250_TOLF_20131011115618.dat',
                    'T1250_TOLI_20131011115618.dat']
        dodge_files = ['dodgy']
        for file in ok_files + dodge_files:
            fh = open(os.path.join(dir, file), 'w')
            fh.close()

        received = self._md.get_files(dir=dir)
        expected = [os.path.join(dir, x) for x in ok_files]
        msg = 'GIS files to process not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        for file in ok_files + dodge_files:
            os.remove(os.path.join(dir, file))

        os.removedirs(dir)

    @classmethod
    def tearDownClass(cls):
        cls._md = None
        del cls._md
