import unittest2
import datetime
import tempfile
import os

import top
from top.utils.files import (copy_file,
                             remove_files,
                             get_directory_files_list)


class TestPodTranslator(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._pt = top.PodTranslator()

    def test_init(self):
        """Initialise an PodTranslator object.
        """
        msg = 'Object is not an top.PodTranslator'
        self.assertIsInstance(self._pt, top.PodTranslator, msg)

    def test_token_generator_datetime_object(self):
        """Verify the token_generator -- datetime object provided
        """
        dt = datetime.datetime(2014, 04, 07, 19, 22, 00, 123456)

        received = self._pt.token_generator(dt)
        expected = '03968625201'
        msg = 'token_generator with datetime object error'
        self.assertEqual(received, expected, msg)

        dt = datetime.datetime(2033, 05, 18, 13, 33, 19, 999999)

        received = self._pt.token_generator(dt)
        expected = '09999999999'
        msg = 'token_generator with datetime object error'
        self.assertEqual(received, expected, msg)

    def test_token_generator_datetime_object_above_threshold(self):
        """Verify the token_generator -- datetime object above threshold
        """
        dt = datetime.datetime(2033, 05, 18, 13, 33, 20, 1)

        received = self._pt.token_generator(dt)
        msg = 'token_generator with datetime above threshold error'
        self.assertIsNone(received, msg)

    def test_token_generator_current_time(self):
        """Verify the token_generator -- current_time.
        """
        received = self._pt.token_generator()
        msg = 'token_generator using current time'
        self.assertIsNotNone(received, msg)

    def test_process(self):
        """Verify a processing loop.
        """
        # Place a copy of the test files in temp directory.
        dir = tempfile.mkdtemp()
        test_file = os.path.join('top',
                                 'tests',
                                 'files',
                                 'NSW_VANA_REF_20131121065550.txt')
        proc_file = os.path.join(dir, os.path.basename(test_file))
        copy_file(test_file, proc_file)
        sig_files = ['P3014R0-00007342.ps', 'P3014R0-00007343.ps']
        for f in sig_files:
            fh = open(os.path.join(dir, f), 'w')
            fh.close()

        # Original signature files should not exist.
        received = self._pt.process(file=proc_file, column='JOB_KEY')
        msg = 'POD translation processing loop error'
        for f in sig_files:
            self.assertFalse(os.path.exists(os.path.join(dir, f)))

        # Check that the translated file was produced.
        received = os.path.exists('%s.xlated' % proc_file)
        msg = 'Translated file error'
        self.assertTrue(received, msg)

        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    def test_process_missing_column(self):
        """Verify a processing loop -- missing column.
        """
        # Place a copy of the test files in temp directory.
        dir = tempfile.mkdtemp()
        test_file = os.path.join('top',
                                 'tests',
                                 'files',
                                 'NSW_VANA_REF_20131121065550.txt')
        proc_file = os.path.join(dir, os.path.basename(test_file))
        copy_file(test_file, proc_file)

        received = self._pt.process(file=proc_file, column='banana')
        expected = []
        msg = 'POD translation processing loop error -- bad column value'
        self.assertListEqual(received, expected, msg)

        # Check that the translated file was produced.
        received = os.path.exists('%s.xlated' % proc_file)
        msg = 'Translated file error'
        self.assertFalse(received, msg)

        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    def test_rename_signature_files(self):
        """Rename signature files.
        """
        dir = tempfile.mkdtemp()
        for f in ['P3014R0-00007342', 'P3014R0-00007343']:
            for ext in ['ps', 'png']:
                fh = open(os.path.join(dir, '%s.%s' % (f, ext)), 'w')
                fh.close()

        received = self._pt.rename_signature_files(dir,
                                                   'P3014R0-00007342',
                                                   '03969357938')
        expected = [os.path.join(dir, '%s.%s' % ('03969357938', 'ps')),
                    os.path.join(dir, '%s.%s' % ('03969357938', 'png'))]
        msg = 'rename_signature_files error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    def test_rename_signature_files_dry_run(self):
        """Rename signature files -- dry run.
        """
        dry = True

        dir = tempfile.mkdtemp()
        files = []
        for f in ['P3014R0-00007342', 'P3014R0-00007343']:
            for ext in ['ps', 'png']:
                fh = open(os.path.join(dir, '%s.%s' % (f, ext)), 'w')
                files.append(fh.name)
                fh.close()

        self._pt.rename_signature_files(dir,
                                       'P3014R0-00007342',
                                       '03969357938',
                                       dry)
        received = get_directory_files_list(dir)
        msg = 'rename_signature_files dry run error'
        self.assertListEqual(sorted(received), sorted(files), msg)

        # Clean up.
        remove_files(files)
        os.removedirs(dir)

    @classmethod
    def tearDownClass(cls):
        del cls._pt
