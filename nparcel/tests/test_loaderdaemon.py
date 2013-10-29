import unittest2
import threading

import nparcel


class TestLoaderDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/tests/files/T1250_TOLI_20130828202901.txt'
        cls._exit_event = threading.Event()
        cls._d = nparcel.LoaderDaemon(pidfile=None,
                                      config='nparcel/conf/nparceld.conf')

    def test_init(self):
        """Intialise a LoaderDaemon object.
        """
        msg = 'Not a nparcel.LoaderDaemon object'
        self.assertIsInstance(self._d, nparcel.LoaderDaemon, msg)

    def test_validate_file_priority(self):
        """Validate filename -- Priority.
        """
        received = self._d.validate_file('T1250_TOLP_20130821011327.txt')
        expected = ('tolp', '2013-08-21 01:13:27')
        msg = 'Validated Priority filename parsed values incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_validate_file_fast(self):
        """Validate filename -- Fast.
        """
        received = self._d.validate_file('T1250_TOLF_VIC_20130821011327.txt')
        expected = ('tolf_vic', '2013-08-21 01:13:27')
        msg = 'Validated Fast filename parsed values incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_validate_file_ipec(self):
        """Validate filename -- Ipec.
        """
        received = self._d.validate_file('T1250_TOLI_20130821011327.txt')
        expected = ('toli', '2013-08-21 01:13:27')
        msg = 'Validated Ipec filename parsed values incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_validate_file_dodgy(self):
        """Validate filename -- dodgy.
        """
        received = self._d.validate_file('T1250_xxxx_20130821011327.txt')
        expected = (None, None)
        msg = 'Validated dodgy filename parsed values incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_check_filename(self):
        """Check Nparcel filename format.
        """
        # Priority.
        received = self._d.check_filename('T1250_TOLP_20130904061851.txt')
        msg = 'Priority Nparcel filename should validate True'
        self.assertTrue(received, msg)

        # Fast.
        received = self._d.check_filename('T1250_TOLF_VIC_20130904061851.txt')
        msg = 'Fast VIC Nparcel filename should validate True'
        self.assertTrue(received, msg)

        # Dodgy.
        received = self._d.check_filename('T1250_dodgy_20130904061851.txt')
        msg = 'Dodgy Nparcel filename should validate False'
        self.assertFalse(received, msg)

    def test_start(self):
        """Start loop.
        """
        # Note: were not testing behaviour here but check that we have
        # one of each, success/error/other.
        old_file = self._d.file
        old_dry = self._d.dry

        self._d.set_dry()
        self._d.set_file(self._file)
        self._d._start(self._exit_event)

        # Clean up.
        self._d.set_file(old_file)
        self._d.set_dry(old_dry)

    @classmethod
    def tearDownClass(cls):
        del cls._file
        del cls._exit_event
        cls._d = None
        del cls._d
