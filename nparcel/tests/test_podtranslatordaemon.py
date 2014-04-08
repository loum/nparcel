import unittest2
import os
import tempfile

import nparcel
from nparcel.utils.files import (copy_file,
                                 remove_files)


class TestPodTranslatorDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        dir = os.path.join('nparcel', 'tests', 'files')
        cls._file = os.path.join(dir, 'NSW_VANA_REF_20131121065550.txt')
        cls._ptd = nparcel.PodTranslatorDaemon(pidfile=None)

        cls._dir = tempfile.mkdtemp()
        cls._ptd.set_in_dirs([cls._dir])
        cls._ptd.set_file_formats(['.*_REF_\d{14}\.txt$'])

    def test_init(self):
        """Intialise a PodTranslatorDaemon object.
        """
        msg = 'Not a nparcel.PodTranslatorDaemon object'
        self.assertIsInstance(self._ptd, nparcel.PodTranslatorDaemon, msg)

    def test_start_dry_pass(self):
        """PodTranslator _start processing loop -- dry pass.
        """
        target_file = os.path.join(self._dir, os.path.basename(self._file))
        copy_file(self._file, target_file)

        old_file = self._ptd.file
        old_dry = self._ptd.dry

        self._ptd.set_file(target_file)
        self._ptd.set_dry()
        self._ptd._start(self._ptd.exit_event)

        # Clean up.
        self._ptd.set_file(old_file)
        self._ptd.set_dry(old_dry)
        remove_files(target_file)
        self._ptd.exit_event.clear()

    def test_start_batch_pass(self):
        """PodTranslator _start processing loop -- batch pass.
        """
        dry = False

        target_file = os.path.join(self._dir, os.path.basename(self._file))
        copy_file(self._file, target_file)

        old_file = self._ptd.file
        old_dry = self._ptd.dry
        old_batch = self._ptd.batch

        self._ptd.set_file(target_file)
        self._ptd.set_dry(dry)
        self._ptd.set_batch(True)
        self._ptd._start(self._ptd.exit_event)

        # Clean up.
        self._ptd.set_file(old_file)
        self._ptd.set_dry(old_dry)
        self._ptd.set_batch(old_batch)
        remove_files(target_file)
        self._ptd.exit_event.clear()

    @classmethod
    def tearDownClass(cls):
        del cls._ptd
        os.removedirs(cls._dir)
