import unittest2

import nparcel


class TestReporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._identifier = 'tester'
        cls._r = nparcel.Reporter(identifier=cls._identifier)

    def test_init(self):
        """Initialise a Reporter object.
        """
        msg = 'Object is not an nparcel.Reporter'
        self.assertIsInstance(self._r, nparcel.Reporter, msg)

    def test_report(self):
        """Run the reporter.
        """
        old_id = self._r.identifier

        self._r.reset()
        received = self._r.report()
        expected = 'None success:0 error:0 other:0 total:0 - duration:0'
        msg = 'report() return message error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._r.set_identifier(old_id)

    def test_incrementors(self):
        """Increment the counts and report.
        """
        old_id = self._r.identifier

        self._r.reset()
        self._r.set_identifier('counter')
        self._r(True)
        self._r(False)
        self._r(None)

        received = self._r.report()
        expected = 'counter success:1 error:1 other:1 total:3 - duration:0'
        msg = 'report() return message error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._r.reset()
        self._r.set_identifier(old_id)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        del cls._r
        del cls._identifier
