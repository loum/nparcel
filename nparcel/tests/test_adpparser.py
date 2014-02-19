import unittest2
import os

import nparcel


class TestAdpParser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        cls._ap = nparcel.AdpParser()
        test_dir = os.path.join('nparcel', 'tests', 'files')
        test_file = 'ADP-Bulk-Load.csv'
        cls._test_file = os.path.join(test_dir, test_file)

    def test_init(self):
        """Initialise a AdpParser object.
        """
        msg = 'Object is not an nparcel.AdpParser'
        self.assertIsInstance(self._ap, nparcel.AdpParser, msg)

    def test_read(self):
        """Read in the sample csv.
        """
        old_in_files = list(self._ap.in_files)
        self._ap.set_in_files([self._test_file])
        self._ap.read()

        received = self._ap.adp_lookup('V001')
        expected = {'ADP Accepts Parcel Size': 'L',
                    'ADP Name': 'Auburn Newsagency',
                    'Active': '1',
                    'Address': '119 Auburn Road',
                    'Contact': '',
                    'DP Code': 'VHAW050',
                    'Email': 'auburnnewsagency@live.com.au',
                    'Fax': '0398134833',
                    'Latitude': '',
                    'Longitude': '',
                    'Notes': '',
                    'Opening Hours': 'Mon-Fri: 7am-6pm; Sat: 7am-2pm; Sun: 8am-2pm',
                    'Phone': '03 9818 4838',
                    'Postcode': '3123',
                    'State': 'VIC',
                    'Suburb': 'HAWTHORN EAST ',
                    'TP Code': 'V001'}
        msg = 'dp_code ADP lookup error'
        self.assertDictEqual(received, expected, msg)

        # Clean up.
        self._ap.set_in_files(old_in_files)

    @classmethod
    def tearDownMethod(cls):
        cls._test_file = None
        cls._ap = None
