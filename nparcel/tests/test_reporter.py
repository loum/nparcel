import unittest2

import nparcel


class TestReporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_init(self):
        """Initialise a Reporter object.
        """
        identifier = 'tester'
        r = nparcel.Reporter(identifier=identifier)

        msg = 'Object is not an nparcel.Reporter'
        self.assertIsInstance(r, nparcel.Reporter, msg)

        r.report()

    @classmethod
    def tearDownClass(cls):
        pass
