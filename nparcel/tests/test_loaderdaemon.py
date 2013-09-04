import unittest2

import nparcel


class TestLoaderDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
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

    @classmethod
    def tearDownClass(cls):
        cls._d = None
