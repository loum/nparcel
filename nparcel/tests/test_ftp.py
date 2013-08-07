import unittest2

import nparcel


class TestFtp(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._ftp = nparcel.Ftp()

    def test_init(self):
        """Initialise an FTP object.
        """
        msg = 'Object is not an nparcel.Ftp'
        self.assertIsInstance(self._ftp, nparcel.Ftp, msg)

    @classmethod
    def tearDownClass(cls):
        cls._ftp = None
