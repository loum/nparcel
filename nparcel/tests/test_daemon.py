import unittest2

import nparcel


class TestDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_init(self):
        """Intialise a Daemon object.
        """
        d = nparcel.Daemon(pidfile=None,
                           config='nparcel/conf/nparceld.conf')
        msg = 'Not a nparcel.Daemon object'
        self.assertIsInstance(d, nparcel.Daemon, msg)

    @classmethod
    def tearDownClass(cls):
        pass
