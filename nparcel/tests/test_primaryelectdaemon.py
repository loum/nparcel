import unittest2
import tempfile
import os

import nparcel
from nparcel.utils.files import remove_files


class TestPrimaryElectDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf_file = 'nparcel/conf/nparceld.conf'
        cls._d = nparcel.PrimaryElectDaemon(pidfile=None, config=conf_file)
        test_dir = 'nparcel/tests/files'
        test_file = 'mts_delivery_report_20131018100758.csv'
        cls._test_file = os.path.join(test_dir, test_file)

    def test_init(self):
        """Intialise a PrimaryElectDaemon object.
        """
        msg = 'Not a nparcel.PrimaryElectDaemon object'
        self.assertIsInstance(self._d, nparcel.PrimaryElectDaemon, msg)

    def test_start(self):
        """Primary Elect _start processing loop.
        """
        self._d.set_dry()
        self._d.set_file(self._test_file)
        self._d._start(self._d.exit_event)

    def test_validate_file_not_mts_format(self):
        """Parse non-MTS formatted file.
        """
        f_obj = tempfile.NamedTemporaryFile()
        mts_file = f_obj.name

        received = self._d.validate_file(mts_file)
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

        received = self._d.validate_file(mts_file)
        msg = 'Dodgy MTS file shoould not validate'
        self.assertTrue(received)

        # Clean up.
        remove_files(mts_file)
        os.removedirs(dir)

    @classmethod
    def tearDownClass(cls):
        cls._d = None
        cls._test_file = None
        del cls._test_file
