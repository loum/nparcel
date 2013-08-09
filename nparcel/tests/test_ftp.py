import unittest2

import nparcel


class TestFtp(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._ftp = nparcel.Ftp(config_file='nparcel/conf/npftp.conf')

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

    @classmethod
    def tearDownClass(cls):
        cls._ftp = None
