import unittest2
import tempfile
import os

import nparcel
from nparcel.utils.files import remove_files


class TestPrimaryElectDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._ped = nparcel.PrimaryElectDaemon(pidfile=None)

        cls._report_in_dirs = tempfile.mkdtemp()
        cls._ped.set_report_in_dirs([cls._report_in_dirs])

        cls._test_dir = 'nparcel/tests/files'
        cls._test_file = 'mts_delivery_report_20131018100758.csv'
        cls._test_file = os.path.join(cls._test_dir, cls._test_file)

    def test_init(self):
        """Intialise a PrimaryElectDaemon object.
        """
        msg = 'Not a nparcel.PrimaryElectDaemon object'
        self.assertIsInstance(self._ped, nparcel.PrimaryElectDaemon, msg)

    def test_start(self):
        """Primary Elect _start processing loop.
        """
        self._ped.set_dry()
        self._ped.set_file(self._test_file)
        self._ped._start(self._ped.exit_event)

    def test_validate_file_not_mts_format(self):
        """Parse non-MTS formatted file.
        """
        f_obj = tempfile.NamedTemporaryFile()
        mts_file = f_obj.name

        received = self._ped.validate_file(mts_file)
        msg = 'Dodgy MTS file shoould not validate'
        self.assertFalse(received)

    def test_validate_file(self):
        """Parse MTS formatted file.
        """
        dir = tempfile.mkdtemp()
        f = open(os.path.join(dir,
                 'mts_delivery_report_20131018100758.csv'), 'w')
        mts_file = f.name
        f.close()

        received = self._ped.validate_file(mts_file)
        msg = 'Dodgy MTS file shoould not validate'
        self.assertTrue(received)

        # Clean up.
        remove_files(mts_file)
        os.removedirs(dir)

    def test_get_files(self):
        """Get report files.
        """
        # Seed some files.
        old_mts_files = ['mts_delivery_report_20131018100755.csv',
                         'mts_delivery_report_20131018100756.csv',
                         'mts_delivery_report_20131018100757.csv']
        mts_file = ['mts_delivery_report_20131018100758.csv']
        for file in old_mts_files + mts_file:
            fh = open(os.path.join(self._report_in_dirs, file), 'w')
            fh.close()

        received = self._ped.get_files()
        expected = [os.path.join(self._report_in_dirs, mts_file[0])]
        msg = 'MTS report files from get_files() error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        files = old_mts_files + mts_file
        remove_files([os.path.join(self._report_in_dirs, x) for x in files])

    def test_get_files_empty_report_dir(self):
        """Get report files -- empty report directory.
        """
        received = self._ped.get_files()
        expected = []
        msg = 'Report files from get_files() error'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._ped = None
        cls._test_file = None
        del cls._test_file

        os.removedirs(cls._report_in_dirs)
