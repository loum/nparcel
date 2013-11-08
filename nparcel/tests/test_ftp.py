import unittest2
import os
import tempfile

import nparcel
from nparcel.utils.files import remove_files


class TestFtp(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._ftp = nparcel.Ftp(config_file='nparcel/conf/npftp.conf')
        cls._test_dir = 'nparcel/tests/files'
        cls._priority_file = os.path.join(cls._test_dir,
                                          'VIC_VANA_REP_20131108145146.txt')

        # Create a temporary directory structure.
        cls._dir = tempfile.mkdtemp()
        cls._archive_dir = tempfile.mkdtemp()
        cls._ftp.set_archive_dir(cls._archive_dir)

    def test_init(self):
        """Initialise an FTP object.
        """
        msg = 'Object is not an nparcel.Ftp'
        self.assertIsInstance(self._ftp, nparcel.Ftp, msg)

    def test_parse_config_items(self):
        """Verify required configuration items.
        """
        self._ftp._parse_config()

        # Check against expected config items.
        msg = 'Transfer sections not as expected'
        received = self._ftp.xfers
        expected = ['ftp_priority', 'ftp_other']
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Archive directory.
        msg = 'Archive directory not as expected'
        received = self._ftp.archive_dir
        expected = '/data/nparcel/archive/ftp'
        self.assertEqual(received, expected, msg)

    def test_get_report_file_no_files(self):
        """Check directory for report files -- no files defined.
        """
        received = []
        for file in self._ftp.get_report_file(self._dir):
            received.append(file)
        msg = 'No reports should be found in an empty directory'
        self.assertListEqual(received, [], msg)

    def test_get_report_file(self):
        """Check directory for report files -- valid file defined.
        """
        filter = 'VIC_VANA_REP_\d{14}\.txt'
        received = []
        for file in self._ftp.get_report_file(self._test_dir, filter):
            received.append(file)
        expected = [os.path.join(self._test_dir,
                                 'VIC_VANA_REP_20131108145146.txt')]
        msg = 'Priority report file should be found in listing'
        self.assertListEqual(received, expected, msg)

        del (received[:], expected[:])
        received = expected = []
        filter = 'VIC_VANA_REI_\d{14}\.txt'
        received = []
        for file in self._ftp.get_report_file(self._test_dir, filter):
            received.append(file)
        expected = [os.path.join(self._test_dir,
                                 'VIC_VANA_REI_20131108145146.txt')]
        msg = 'Ipec report file should be found in listing'
        self.assertListEqual(received, expected, msg)

    def test_get_report_file_ids(self):
        """Check directory for report files -- valid file defined.
        """
        report = os.path.join(self._dir, 'VIC_VANA_REP_20130812140736.txt')
        fh = open(report, 'w')
        fh.write('REF1|JOB_KEY|PICKUP_TIME|PICKUP_POD|IDENTITY_TYPE|IDENTITY_DATA\n')
        fh.write('ALHZ104346|5|2013-02-01 01:23:45|UNCOLLECTED PARCEL DATACLEANUP|Other|0000')
        fh.close()

        received = self._ftp.get_report_file_ids(report)
        expected = ['5']
        msg = 'Report file should be found in directory'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        remove_files(report)

    def test_archive_file(self):
        """Archive file.
        """
        #temp_file = tempfile.NamedTemporaryFile()
        #temp_file_name = temp_file.name
        test_file = os.path.join(self._dir, 'tester')
        fh = open(test_file, 'w')
        fh.close()

        received = self._ftp.archive_file(test_file, dry=False)
        msg = 'File archive should return True'
        self.assertTrue(received, msg)

        # Check the archive directory.
        files = os.listdir(self._ftp.archive_dir)
        received = [os.path.join(self._ftp.archive_dir, x) for x in files]
        expected = [os.path.join(self._ftp.archive_dir,
                                 os.path.basename(test_file))]
        msg = 'Archive directory contents not as expected'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        remove_files(received)

    @classmethod
    def tearDownClass(cls):
        del cls._test_dir
        del cls._priority_file
        cls._ftp = None
        del cls._ftp
        os.removedirs(cls._dir)
        del cls._dir
        os.removedirs(cls._archive_dir)
        del cls._archive_dir
