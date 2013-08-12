import unittest2
import os
import tempfile

import nparcel


class TestFtp(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._ftp = nparcel.Ftp(config_file='nparcel/conf/npftp.conf')

        # Create a temporary directory structure.
        cls._dir = tempfile.mkdtemp()

    def test_init(self):
        """Initialise an FTP object.
        """
        msg = 'Object is not an nparcel.Ftp'
        self.assertIsInstance(self._ftp, nparcel.Ftp, msg)

    def test_parse_config_no_file(self):
        """Parse config with no file provided.
        """
        old_config = self._ftp.config_file
        self._ftp.set_config_file(None)

        self.assertRaises(SystemExit, self._ftp._parse_config)

        # Cleanup.
        self._ftp.set_config_file(old_config)

    def test_parse_config_items(self):
        """Verify required configuration items.
        """
        self._ftp._parse_config()

        # Check against expected config items.
        msg = 'Transfer sections not as expected'
        received = self._ftp.xfers
        expected = ['ftp_priority', 'ftp_other']
        self.assertListEqual(sorted(received), sorted(expected), msg)

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
        # Fudge a report file name.
        report = os.path.join(self._dir, 'VIC_VANA_REP_20130812140736.txt')
        fh = open(report, 'w')
        fh.close()

        received = []
        for file in self._ftp.get_report_file(self._dir):
            received.append(file)
        expected = [report]
        msg = 'Report file should be found in directory'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        os.remove(report)

    def test_get_report_file(self):
        """Check directory for report files -- valid file defined.
        """
        # Fudge a report file name.
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
        os.remove(report)

    @classmethod
    def tearDownClass(cls):
        cls._ftp = None
        os.removedirs(cls._dir)
        cls._dir = None
