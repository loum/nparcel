import unittest2
import os
import tempfile

import nparcel
from nparcel.utils.files import (remove_files,
                                 copy_file,
                                 get_directory_files_list)


class TestAdp(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._adp = nparcel.Adp()

        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')

        db = cls._adp.db
        fixtures = [{'db': db.agent, 'fixture': 'agents.py'},
                    {'db': db.parcel_size, 'fixture': 'parcel_sizes.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Initialise an Adp object.
        """
        msg = 'Object is not a nparcel.Adp'
        self.assertIsInstance(self._adp, nparcel.Adp, msg)

    def test_process_dry_run(self):
        """Check processing -- dry run.
        """
        dry = True

        test_dir = os.path.join('nparcel', 'tests', 'files')
        csv_file = 'ADP-Bulk-Load.csv'
        test_file = os.path.join(test_dir, csv_file)

        dir = tempfile.mkdtemp()
        in_file = os.path.join(dir, os.path.basename(test_file))
        copy_file(test_file, os.path.join(dir, in_file))

        old_headers = self._adp.headers

        # Start processing.
        headers = {'code': 'TP Code',
                   'dp_code':  'DP Code',
                   'name': 'ADP Name'}
        code = {}
        code['V010'] = {'TP Code': 'V010',
                        'DP Code': 'VCLA005',
                        'ADP Name': 'Clayton Newsagency',
                        'Address': '345 Clayton Road',
                        'Suburb': 'CLAYTON',
                        'State': 'VIC',
                        'Postcode': '3168'}
        self._adp.set_headers(headers)
        received = self._adp.process(code='V0101',
                                     values=code['V010'],
                                     dry=dry)
        msg = 'ADP line item processing should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._adp.db.rollback()
        self._adp.set_headers(old_headers)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    def test_extract_values(self):
        """Extract values from parsed agent dictionary structure.
        """
        raw_dict = {'Fax': 'agent.fax_nbr',
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

        old_headers = self._adp.headers
        headers = {'code': 'TP Code',
                   'dp_code':  'DP Code',
                   'name': 'ADP Name'}
        self._adp.set_headers(headers)

        received = self._adp.extract_values(raw_dict)
        expected = {'dp_code': 'agent.dp_code',
                    'name': 'agent.name',
                    'code': 'agent.code'}
        msg = 'Extracted headers incorrect'
        self.assertDictEqual(received, expected, msg)

        # Clean up.
        self._adp.set_headers(old_headers)

    def test_sanitise_status(self):
        """Sanitise the "agent.status" column.
        """
        received = self._adp.sanitise({'status': '1'})
        expected = {'status': 1}
        msg = 'Sanitise status "1" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'status': 'NO'})
        expected = {'status': 2}
        msg = 'Sanitise status "NO" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'status': 'YES'})
        expected = {'status': 1}
        msg = 'Sanitise status "YES" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'banana': 'YES'})
        expected = {'banana': 'YES'}
        msg = 'Sanitise status not defined error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'banana': 'YES'})
        expected = {'banana': 'YES'}
        msg = 'Sanitise status not defined error'
        self.assertEqual(received, expected, msg)

    def test_validate_status(self):
        """Validate the "agent.status" column.
        """
        received = self._adp.validate({'status': 2})
        msg = 'Validate status as integer error'
        self.assertTrue(received, msg)

        received = self._adp.validate({'status': '1'})
        msg = 'Validate status as a non-integer error'
        self.assertFalse(received, msg)

    def test_validate_postcode(self):
        """Validate the "agent.postcode" column.
        """
        received = self._adp.validate({'postcode': '3000',
                                       'state': 'VIC'})
        msg = 'Validate postcode, state should be True'
        self.assertTrue(received, msg)

        received = self._adp.validate({'postcode': '4000',
                                       'state': 'VIC'})
        msg = 'Validate postcode, state should be False'
        self.assertFalse(received, msg)

        received = self._adp.validate({'postcode': '4000'})
        msg = 'Validate postcode, missing state should be False'
        self.assertTrue(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._adp = None
