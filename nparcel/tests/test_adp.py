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
        self._adp.set_headers(headers)
        self._adp.process(in_files=[in_file], dry=dry)

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

    @classmethod
    def tearDownClass(cls):
        cls._adp = None
