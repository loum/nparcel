import unittest2

import nparcel


class TestLoaderDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_init(self):
        """Intialise a LoaderDaemon object.
        """
        d = nparcel.LoaderDaemon(pidfile=None,
                                 config='nparcel/conf/nparceld.conf')
        msg = 'Not a nparcel.LoaderDaemon object'
        self.assertIsInstance(d, nparcel.LoaderDaemon, msg)

    @classmethod
    def tearDownClass(cls):
        pass
