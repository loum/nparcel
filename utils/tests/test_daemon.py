import unittest2
import time
import os.path

import nparcel.utils
from nparcel.utils.files import dummy_filesystem


class DummyDaemon(nparcel.utils.Daemon):
    def _start(self, event):
        while True:
            time.sleep(1)


class TestDaemon(unittest2.TestCase):

    def setUp(self):
        # Create a location for our PID.
        self._temp_fs = dummy_filesystem()
        self._pid_file = self._temp_fs.name
        self._temp_fs.close()

    def test_init_of_abstract_class(self):
        """Test initialisation of the abstract Daemon class.
        """
        with self.assertRaises(TypeError):
            nparcel.utils.Daemon(self._pid_file)

    def test_init_with_no_arguments(self):
        """Test initialisation with no arguments.
        """
        with self.assertRaises(TypeError):
            DummyDaemon()

    def test_init_with_pidfile_none(self):
        """Test exception generation if no PID file is specified.
        """
        daemon = DummyDaemon(pidfile=None)
        with self.assertRaises(nparcel.utils.DaemonError):
            daemon._start_daemon()

    def test_init_with_unwritable_pid_file(self):
        """Test initialisation with unwritable PID file.
        """
        # But won't work if run as root :-(.
        unwritable_pid_file = '/pid'
        daemon = DummyDaemon(pidfile=unwritable_pid_file)

        with self.assertRaisesRegexp(nparcel.utils.DaemonError,
                                    'Cannot write to PID file: *'):
            daemon.start()

    def test_start_with_existing_pid_file(self):
        """Test start with existing PID file.
        """
        # Open local instance of a PID file to simulate existing file.
        # PID file contents are empty.
        temp_fs = dummy_filesystem()
        pid_file = temp_fs.name

        # Attempt to set up the daemon.
        with self.assertRaisesRegexp(nparcel.utils.DaemonError,
                                     'Error reading PID file: *'):
            DummyDaemon(pidfile=pid_file)

        # Clean up.  
        temp_fs.close()

    def test_init_with_valid_pid_file(self):
        """Test initialisation of the Daemon with valid PID file.
        """
        daemon = DummyDaemon(pidfile=self._pid_file,
                             term_parent=False)
        msg = 'PID file error -- expected "%s", received "%s"'
        expected = self._pid_file
        received = daemon.pidfile
        self.assertEqual(expected, received, msg % (expected, received))

        # In this case, the PID file is empty which suggests that state
        # of process is idle.
        msg = 'Initial PID should be "None"'
        received = daemon.pid
        expected = None
        self.assertEqual(received, expected, msg)

        # TODO: It would be really nice to test the start of the daemon.

    def test_stop_with_pid_file_missing(self):
        """Test stop around missing PID file.
        """
        daemon = DummyDaemon(pidfile=self._pid_file)
        msg = 'Daemon stop status for missing PID file should be False'
        self.assertFalse(daemon.stop(), msg)

        msg = 'PID file should be removed if stop attempt on non-process'
        self.assertFalse(os.path.exists(self._pid_file), msg)

    def test_stop_non_existent_pid(self):
        """Test stop of an non-existent PID file.
        """
        # Open local instance of a PID file to simulate empty file.
        # This file will be deleted by the stop() method make it persist
        # on the filesystem so that temporary file doesn't barf.
        temp_fs = dummy_filesystem(content='999999')
        temp_fs.delete = False
        pid_file = temp_fs.name

        # Set up the daemon.
        daemon = DummyDaemon(pidfile=pid_file)
        msg = 'Daemon stop status dodgy PID should be False'
        self.assertFalse(daemon.stop(), msg)

        # Check that the PID file was removed.
        msg = 'PID file "%s" was not removed after dodgy PID' % pid_file
        self.assertFalse(os.path.exists(pid_file), msg)

    def test_status_running_inline_process(self):
        """Test status of PID for an active inline process.
        """
        # Can only test this with the inline daemon instance.
        # The daemon variant *should* behave the same way.
        daemon = DummyDaemon(pidfile=None)
        daemon.start()

        msg = 'Status check of inline process should return True'
        received = daemon.status()
        self.assertTrue(received, msg)

        # Try again to make sure the previous check did not kill process.
        msg = 'Repeat status check of inline process should return True'
        received = daemon.status()
        self.assertTrue(received, msg)

        daemon.stop()

    def test_status_invalid_inline_process(self):
        """Test status of PID for an inactive inline process.
        """
        # Fudge an invalid PID.
        daemon = DummyDaemon(pidfile=None)
        daemon.pid = 99999

        msg = 'Status check on an invalid PID should return false'
        self.assertFalse(daemon.status(), msg)

    def test_status_idle_inline_process(self):
        """Test status of PID for an iidle inline process.
        """
        daemon = DummyDaemon(pidfile=None)

        msg = 'Status check of idle inline process should return False'
        self.assertFalse(daemon.status(), msg)

    def test_status_call_before_inline_process_start(self):
        """Test that status call before start does not leave PID file.
        """
        # Check that PID file is not present.
        msg = 'PID file BEFORE DummyDaemon initialisation should not exist'
        self.assertFalse(os.path.exists(self._pid_file), msg)

        daemon = DummyDaemon(pidfile=self._pid_file)

        # PID file should still not be present.
        msg = 'PID file AFTER DummyDaemon initialisation should not exist'
        self.assertFalse(os.path.exists(self._pid_file), msg)

        # Run a status check and confirm that the PID file is still not
        # present.
        daemon.status()
        msg = 'PID file AFTER DummyDaemon status check should not exist'
        self.assertFalse(os.path.exists(self._pid_file), msg)

    def tearDown(self):
        self._pid_file = None
        self._temp_fs = None
