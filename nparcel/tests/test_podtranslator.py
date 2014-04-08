import unittest2
import datetime
import tempfile
import os

import nparcel
from nparcel.utils.files import (copy_file,
                                 remove_files,
                                 get_directory_files_list)


class TestPodTranslator(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._pt = nparcel.PodTranslator()

    def test_init(self):
        """Initialise an PodTranslator object.
        """
        msg = 'Object is not an nparcel.PodTranslator'
        self.assertIsInstance(self._pt, nparcel.PodTranslator, msg)

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
        test_file = os.path.join('nparcel',
                                 'tests',
                                 'files',
                                 'NSW_VANA_REF_20131121065550.txt')
        proc_file = os.path.join(dir, os.path.basename(test_file))
        copy_file(test_file, proc_file)

        received = self._pt.process(file=proc_file, column='JOB_KEY')
        expected = ['P3014R0-00007342', 'P3014R0-00007343']
        msg = 'POD translation processing loop error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

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
        test_file = os.path.join('nparcel',
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

    @classmethod
    def tearDownClass(cls):
        del cls._pt
