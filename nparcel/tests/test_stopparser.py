import unittest2

import nparcel


class TestStopParser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._sp = nparcel.StopParser()
        cls._test_file = 'nparcel/tests/stop_report.csv'

    def test_init(self):
        """Initialise a StopParser object.
        """
        sp = nparcel.StopParser()
        msg = 'Object is not an nparcel.StopParser'
        self.assertIsInstance(sp, nparcel.StopParser, msg)

    def test_read(self):
        """Read in the sample csv.
        """
        self._sp.set_in_file(self._test_file)

        received = []
        for con in self._sp.read('Con Note'):
            received.append(con)
            if len(received) > 10:
                break
        expected = ['GOLD0000000024',
                    'GOLW000007',
                    'GOLW000680',
                    'GOLW000015',
                    'GOLW000625',
                    'GOLD0000005050',
                    'GOLW000524',
                    'GOLW001883',
                    'GOLW000120',
                    'GOLW001352',
                    'GOLW001000']
        msg = 'Parsed connote list incorrect'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._sp.set_in_file(None)

    @classmethod
    def tearDownClass(cls):
        cls._sp = None
        del cls._sp
