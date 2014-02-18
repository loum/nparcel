import unittest2
import tempfile
import os

import nparcel
from nparcel.utils.files import (copy_file,
                                 remove_files,
                                 get_directory_files_list)


class TestAdpDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._adpd = nparcel.AdpDaemon(pidfile=None)
        test_dir = os.path.join('nparcel', 'tests', 'files')
        xlsv_file = 'ADP-Bulk-Load.xlsx'
        cls._test_file = os.path.join(test_dir, xlsv_file)

    def test_init(self):
        """Initialise a AdpDaemon object.
        """
        msg = 'Not a nparcel.AdpDaemon object'
        self.assertIsInstance(self._adpd, nparcel.AdpDaemon, msg)

    def test_start_dry_loop(self):
        """On Delivery _start dry loop.
        """
        old_dry = self._adpd.dry
        old_file = self._adpd.file

        dir = tempfile.mkdtemp()
        test_file = os.path.join(dir, os.path.basename(self._test_file))
        copy_file(self._test_file, os.path.join(dir, test_file))

        # Start processing.
        self._adpd.set_dry()
        self._adpd.set_file(test_file)
        self._adpd._start(self._adpd.exit_event)

        # Clean up.
        self._adpd._exit_event.clear()
        self._adpd.set_dry(old_dry)
        self._adpd.set_file(old_file)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    def test_start_dry_loop_dir_based(self):
        """On Delivery _start dry loop - directory file input.
        """
        old_dry = self._adpd.dry
        old_adp_in_dir = self._adpd.adp_in_dirs
        old_adp_in_dirs = self._adpd.adp_in_dirs

        dir = tempfile.mkdtemp()
        test_file = os.path.join(dir, os.path.basename(self._test_file))
        copy_file(self._test_file, test_file)

        # Start processing.
        self._adpd.set_dry()
        self._adpd.set_adp_in_dirs([dir])
        self._adpd._start(self._adpd.exit_event)

        # Clean up.
        self._adpd.set_dry(old_dry)
        self._adpd._exit_event.clear()
        self._adpd.set_adp_in_dirs(old_adp_in_dirs)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    @classmethod
    def tearDownClass(cls):
        cls._adpd = None
        cls._test_file = None
