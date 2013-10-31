import unittest2
import threading
import tempfile
import os

import nparcel
from nparcel.utils.files import (copy_file,
                                 remove_files)


class TestFilterDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/tests/files/T1250_TOLI_20130828202901.txt'
        cls._exit_event = threading.Event()
        cls._fd = nparcel.FilterDaemon(pidfile=None,
                                       config='nparcel/conf/nparceld.conf')

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
        self._fd._start(self._exit_event)

        # Clean up.
        self._fd.set_file(old_file)
        self._fd.set_dry(old_dry)
        self._exit_event.clear()

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

        received = self._fd.get_files(in_dir)
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

    @classmethod
    def tearDownClass(cls):
        del cls._file
        del cls._exit_event
        cls._fd = None
        del cls._fd
