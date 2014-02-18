import unittest2
import os

import nparcel


class TestAdpParser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
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

        received = self._ap.adp_lookup('agent.code')
        expected = {'Fax': 'agent.fax_nbr',
                    'TP Code': 'agent.code',
                    'ADP Accepts Parcel Size':
                    'agent.parcel_size_code',
                    'Phone': 'agent.phone_nbr',
                    'Notes': 'agent.notes',
                    'Latitude': 'agent.latitude',
                    'State': 'agent.state',
                    'Longtitude': 'agent.longtitude',
                    'Suburb': 'agent.suburb',
                    'ADP Name': 'agent.name',
                    'Contact': 'agent.contact_name',
                    'DP Code': 'agent.dp_code',
                    'Postcode': 'agent.postcode',
                    'Address': 'agent.address',
                    'Opening Hours': 'agent.opening_hours',
                    'Email': 'agent.email',
                    'Active': 'agent.status'}
        msg = 'dp_code ADP lookup error'
        self.assertDictEqual(received, expected, msg)

        # Clean up.
        self._ap.set_in_files(old_in_files)

    @classmethod
    def tearDownMethod(cls):
        cls._test_file = None
        cls._ap = None
