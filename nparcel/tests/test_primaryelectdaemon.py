import unittest2

import nparcel


class TestPrimaryElectDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf_file = 'nparcel/conf/nparceld.conf'
        cls._d = nparcel.PrimaryElectDaemon(pidfile=None,
                                            config=conf_file)

    def test_init(self):
        """Intialise a PrimaryElectDaemon object.
        """
        msg = 'Not a nparcel.PrimaryElectDaemon object'
        self.assertIsInstance(self._d, nparcel.PrimaryElectDaemon, msg)

    @classmethod
    def tearDownClass(cls):
        cls._d = None
