import unittest2
import os
import tempfile
import datetime

import top
from top.utils.files import (copy_file,
                             get_directory_files_list,
                             remove_files)


class TestPodTranslatorDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        dir = os.path.join('top', 'tests', 'files')
        cls._file = os.path.join(dir, 'NSW_VANA_REF_20131121065550.txt')
        cls._ptd = top.PodTranslatorDaemon(pidfile=None)

        cls._dir = tempfile.mkdtemp()
        cls._ptd.set_in_dirs([cls._dir])
        cls._out_dir = tempfile.mkdtemp()
        cls._ptd.set_out_dir(cls._out_dir)
        cls._archive_dir = tempfile.mkdtemp()
        cls._ptd.set_archive_dir(cls._archive_dir)
        cls._ptd.set_file_formats(['.*_REF_\d{14}\.txt$'])

    def test_init(self):
        """Intialise a PodTranslatorDaemon object.
        """
        msg = 'Not a top.PodTranslatorDaemon object'
        self.assertIsInstance(self._ptd, top.PodTranslatorDaemon, msg)

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
        remove_files(get_directory_files_list(self._dir))
        self._ptd.exit_event.clear()

    def test_start_batch_pass(self):
        """PodTranslator _start processing loop -- batch pass.
        """
        dry = False

        target_file = os.path.join(self._dir, os.path.basename(self._file))
        copy_file(self._file, target_file)
        sig_files = [os.path.join(self._dir, 'P3014R0-00007342.ps'),
                     os.path.join(self._dir, 'P3014R0-00007343.ps')]
        for f in sig_files:
            fh = open(f, 'w')
            fh.close

        old_file = self._ptd.file
        old_dry = self._ptd.dry
        old_batch = self._ptd.batch

        self._ptd.set_dry(dry)
        self._ptd.set_batch(True)
        self._ptd._start(self._ptd.exit_event)

        # Check that we have a translated file in the target_dir.
        out_file = os.path.join(self._ptd.out_dir,
                                os.path.basename(target_file))
        received = os.path.exists(out_file)
        msg = 'Translated file error'
        self.assertTrue(received, msg)

        # ... and that the original is archived.
        dmy = datetime.datetime.now().strftime('%Y%m%d')
        archive_dir = os.path.join(self._ptd.archive_dir, dmy)
        arch_file = os.path.join(archive_dir, os.path.basename(target_file))
        received = os.path.exists(arch_file)
        msg = 'Translated file archive error'
        self.assertTrue(received, msg)

        # Clean up.
        self._ptd.set_file(old_file)
        self._ptd.set_dry(old_dry)
        self._ptd.set_batch(old_batch)
        remove_files(get_directory_files_list(self._ptd.out_dir))
        remove_files(get_directory_files_list(archive_dir))
        os.rmdir(archive_dir)
        self._ptd.exit_event.clear()

    def test_start_batch_missing_signature_file(self):
        """PodTranslator _start processing loop -- missing sig files.
        """
        dry = False

        target_file = os.path.join(self._dir, os.path.basename(self._file))
        copy_file(self._file, target_file)

        old_file = self._ptd.file
        old_dry = self._ptd.dry
        old_batch = self._ptd.batch

        self._ptd.set_dry(dry)
        self._ptd.set_batch(True)
        self._ptd._start(self._ptd.exit_event)

        # Check that a translated file exists in the current_dir.
        out_file = os.path.join(self._dir,
                                '%s.xlated' % os.path.basename(target_file))
        received = os.path.exists(out_file)
        msg = 'Translated file error'
        self.assertTrue(received, msg)

        # As this processing failed, original should not be archived.
        dmy = datetime.datetime.now().strftime('%Y%m%d')
        archive_dir = os.path.join(self._ptd.archive_dir, dmy)
        arch_file = os.path.join(archive_dir, os.path.basename(target_file))
        received = os.path.exists(arch_file)
        msg = 'Translated file archive error -- no sig files'
        self.assertFalse(received, msg)

        # ... and moved aside with a .err extension.
        received = os.path.exists('%s.err' % target_file)
        msg = 'Translated file move to .err error'
        self.assertTrue(received, msg)

        # Clean up.
        self._ptd.set_file(old_file)
        self._ptd.set_dry(old_dry)
        self._ptd.set_batch(old_batch)
        remove_files(get_directory_files_list(self._dir))
        self._ptd.exit_event.clear()

    def test_move_signature_files(self):
        """Move signature files.
        """
        source_dir = tempfile.mkdtemp()
        target_dir = tempfile.mkdtemp()
        sig_files = [os.path.join(source_dir, '03970006761.ps'),
                     os.path.join(source_dir, '03970006762.png')]
        for f in sig_files:
            fh = open(f, 'w')
            fh.close

        received = self._ptd.move_signature_files('03970006761',
                                                  source_dir,
                                                  target_dir)
        msg = 'Signature file move error'
        self.assertTrue(received, msg)

        # Check the target file exists.
        received = os.path.exists(os.path.join(target_dir,
                                               '03970006761.ps'))
        self.assertTrue(received, msg)

        # Clean up.
        remove_files(get_directory_files_list(source_dir))
        remove_files(get_directory_files_list(target_dir))
        os.removedirs(source_dir)
        os.removedirs(target_dir)

    def test_move_signature_files_dry_pass(self):
        """Move signature files -- dry pass.
        """
        dry = True

        source_dir = tempfile.mkdtemp()
        target_dir = tempfile.mkdtemp()
        sig_files = [os.path.join(source_dir, '03970006761.ps'),
                     os.path.join(source_dir, '03970006762.png')]
        for f in sig_files:
            fh = open(f, 'w')
            fh.close

        received = self._ptd.move_signature_files('03970006762',
                                                  source_dir,
                                                  target_dir,
                                                  dry=dry)
        msg = 'Signature file move error -- dry run'
        self.assertTrue(received, msg)

        # Check the source file exists.
        received = os.path.exists(os.path.join(source_dir,
                                               '03970006762.png'))
        self.assertTrue(received, msg)

        # Clean up.
        remove_files(get_directory_files_list(source_dir))
        remove_files(get_directory_files_list(target_dir))
        os.removedirs(source_dir)
        os.removedirs(target_dir)

    @classmethod
    def tearDownClass(cls):
        os.removedirs(cls._dir)
        os.removedirs(cls._out_dir)
        os.removedirs(cls._archive_dir)
        del cls._dir
        del cls._out_dir
        del cls._archive_dir
        del cls._ptd
