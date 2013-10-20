import unittest2
import os

import nparcel


class TestStopParser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._sp = nparcel.StopParser()
        test_dir = 'nparcel/tests/files'
        test_file = 'mts_delivery_report_20131018100758.csv'
        cls._test_file = os.path.join(test_dir, test_file)

    def test_init(self):
        """Initialise a StopParser object.
        """
        sp = nparcel.StopParser()
        msg = 'Object is not an nparcel.StopParser'
        self.assertIsInstance(sp, nparcel.StopParser, msg)

    def test_read(self):
        """Read in the sample csv.
        """
        old_in_file = self._sp.in_file
        self._sp.set_in_file(self._test_file)
        self._sp.read()

        # Return known connote.
        received = self._sp.connote_lookup('ARTZ023438')
        msg = 'Known connote should not return None'
        self.assertIsNotNone(received)

        # Return unknown connote.
        received = self._sp.connote_lookup('banana')
        msg = 'Unknown connote should return None'
        self.assertIsNone(received)

        # Check delivered.
        received = self._sp.connote_delivered('GOLW013730')
        msg = 'Undelivered connote should return False'
        self.assertFalse(received)

        # Check delivered.
        received = self._sp.connote_delivered('GOLW012959')
        msg = 'Delivered connote should return True'
        self.assertTrue(received)

        # ... and purge.
        self._sp.purge()

        # Return previously-known connote.
        received = self._sp.connote_lookup('ARTZ023438')
        msg = 'Known connote should now return None'
        self.assertIsNone(received)

        # Cleanup.
        self._sp.set_in_file(old_in_file)

    @classmethod
    def tearDownClass(cls):
        cls._sp = None
        del cls._sp
