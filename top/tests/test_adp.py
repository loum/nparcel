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
        old_delivery_partners = self._adp.delivery_partners
        old_default_passwords = self._adp.default_passwords

        # Start processing.
        headers = {'agent.code': 'TP Code',
                   'agent.dp_code':  'DP Code',
                   'agent.name': 'ADP Name',
                   'delivery_partner.id': 'DP Id',
                   'login_account.username': 'Username'}
        self._adp.set_headers(headers)
        delivery_partners = ['Nparcel',
                             'ParcelPoint',
                             'Toll',
                             'National Storage']
        self._adp.set_delivery_partners(delivery_partners)
        self._adp.set_default_passwords({'nparcel': 'aaaa'})
        code = {}
        code['V010'] = {'TP Code': 'V010',
                        'DP Code': 'VCLA005',
                        'ADP Name': 'Clayton Newsagency',
                        'Address': '345 Clayton Road',
                        'Suburb': 'CLAYTON',
                        'State': 'VIC',
                        'Postcode': '3168',
                        'DP Id': 'Nparcel',
                        'Username': 'VCLA005'}
        received = self._adp.process(code='V0101',
                                     values=code['V010'],
                                     dry=dry)
        msg = 'ADP line item processing should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._adp.db.rollback()
        self._adp.set_headers(old_headers)
        self._adp.set_delivery_partners(old_delivery_partners)
        self._adp.set_default_passwords(old_default_passwords)
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
        received = self._adp.sanitise({'agent.status': '1'})
        expected = {'agent.status': 1,
                    'login_account.status': 1}
        msg = 'Sanitise status "1" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'agent.status': 'NO'})
        expected = {'agent.status': 2,
                    'login_account.status': 1}
        msg = 'Sanitise status "NO" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'agent.status': 'YES'})
        expected = {'agent.status': 1,
                    'login_account.status': 1}
        msg = 'Sanitise status "YES" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'banana': 'YES'})
        expected = {'banana': 'YES',
                    'login_account.status': 1}
        msg = 'Sanitise status not defined error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'banana': 'YES'})
        expected = {'banana': 'YES',
                    'login_account.status': 1}
        msg = 'Sanitise status not defined error'
        self.assertEqual(received, expected, msg)

    def test_sanitise_delivery_partner(self):
        """Sanitise the "delivery_partner.id" column.
        """
        old_delivery_partners = self._adp.delivery_partners

        self._adp.set_delivery_partners(['Nparcel',
                                         'ParcelPoint',
                                         'Toll',
                                         'National Storage'])
        received = self._adp.sanitise({'delivery_partner.id': 'Nparcel'})
        expected = {'delivery_partner.id': 1,
                    'login_account.status': 1,
                    'agent.dp_id': 1}
        msg = 'Sanitise delivery_partner "Nparcel" error'
        self.assertDictEqual(received, expected, msg)

        # Unknown delivery partner.
        received = self._adp.sanitise({'delivery_partner.id': 'banana'})
        expected = {'login_account.status': 1}
        self.assertDictEqual(received, expected, msg)

        # Clean up.
        self._adp.set_delivery_partners(old_delivery_partners)

    def test_sanitise_password(self):
        """Sanitise the "login_account.password" column.
        """
        old_delivery_partners = self._adp.delivery_partners
        old_default_passwords = self._adp.default_passwords

        self._adp.set_delivery_partners(['Nparcel',
                                         'ParcelPoint',
                                         'Toll',
                                         'National Storage'])
        self._adp.set_default_passwords({'nparcel': 'aaaa'})

        received = self._adp.sanitise({'delivery_partner.id': 'Nparcel'})
        expected = {'delivery_partner.id': 1,
                    'login_account.password': 'aaaa',
                    'login_account.status': 1,
                    'agent.dp_id': 1}
        msg = 'Sanitise password error'
        self.assertDictEqual(received, expected, msg)

        received = self._adp.sanitise({'delivery_partner.id': 'banana'})
        expected = {'login_account.status': 1}
        msg = 'Sanitise missing password error'
        self.assertDictEqual(received, expected, msg)

        # Clean up.
        self._adp.set_delivery_partners(old_delivery_partners)
        self._adp.set_default_passwords(old_default_passwords)

    def test_sanitise_login_account_status(self):
        """Sanitise the "login_account.status" column.
        """
        received = self._adp.sanitise({'login_account.status': 'YES'})
        expected = {'login_account.status': 1}
        msg = 'Sanitise login_account.status "YES" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'login_account.status': 'Y'})
        expected = {'login_account.status': 1}
        msg = 'Sanitise login_account.status "Y" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'login_account.status': 'NO'})
        expected = {'login_account.status': 0}
        msg = 'Sanitise login_account.status "NO" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'login_account.status': 'N'})
        expected = {'login_account.status': 0}
        msg = 'Sanitise login_account.status "N" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({})
        expected = {'login_account.status': 1}
        msg = 'Sanitise login_account.status not defined error'
        self.assertEqual(received, expected, msg)

    def test_validate_status(self):
        """Validate the "agent.status" column.
        """
        received = self._adp.validate({'agent.status': 2,
                                       'delivery_partner.id': 1,
                                       'login_account.username': 'VHAW050',
                                       'login_account.password': 'aaaa'})
        msg = 'Validate status as integer error'
        self.assertTrue(received, msg)

        received = self._adp.validate({'agent.status': '1',
                                       'delivery_partner.id': 1,
                                       'login_account.username': 'VHAW050',
                                       'login_account.password': 'aaaa'})
        msg = 'Validate status as a non-integer error'
        self.assertFalse(received, msg)

    def test_validate_postcode(self):
        """Validate the "agent.postcode" column.
        """
        received = self._adp.validate({'agent.postcode': '3000',
                                       'agent.state': 'VIC',
                                       'delivery_partner.id': 1,
                                       'login_account.username': 'VHAW050',
                                       'login_account.password': 'aaaa'})
        msg = 'Validate postcode, state should be True'
        self.assertTrue(received, msg)

        received = self._adp.validate({'agent.postcode': '4000',
                                       'agent.state': 'VIC',
                                       'delivery_partner.id': 1,
                                       'login_account.username': 'VHAW050',
                                       'login_account.password': 'aaaa'})
        msg = 'Validate postcode, state should be False'
        self.assertFalse(received, msg)

        received = self._adp.validate({'agent.postcode': '4000',
                                       'delivery_partner.id': 1,
                                       'login_account.username': 'VHAW050',
                                       'login_account.password': 'aaaa'})
        msg = 'Validate postcode, missing state should be False'
        self.assertTrue(received, msg)

    def test_validate_delivery_partner(self):
        """Validate the "delivery_partner.id" column.
        """
        received = self._adp.validate({'agent.postcode': '3000',
                                       'agent.state': 'VIC',
                                       'delivery_partner.id': 1,
                                       'login_account.username': 'VHAW050',
                                       'login_account.password': 'aaaa'})
        msg = 'Validate delivery_partner.id of 1 should be True'
        self.assertTrue(received, msg)

        received = self._adp.validate({'agent.postcode': '3000',
                                       'agent.state': 'VIC',
                                       'login_account.username': 'VHAW050',
                                       'login_account.password': 'aaaa'})
        msg = 'Validate missing delivery_partner.id key should be False'
        self.assertFalse(received, msg)

    def test_validate_username(self):
        """Validate the "login_account.username" column.
        """
        received = self._adp.validate({'agent.postcode': '3000',
                                       'agent.state': 'VIC',
                                       'delivery_partner.id': 1,
                                       'login_account.username': 'VHAW050',
                                       'login_account.password': 'aaaa'})
        msg = 'Validate username should be True'
        self.assertTrue(received, msg)

        received = self._adp.validate({'agent.postcode': '3000',
                                       'agent.state': 'VIC',
                                       'delivery_partner.id': 1,
                                       'login_account.password': 'aaaa'})
        msg = 'Validate missing username should be False'
        self.assertFalse(received, msg)

        received = self._adp.validate({'agent.postcode': '3000',
                                       'agent.state': 'VIC',
                                       'delivery_partner.id': 1,
                                       'login_account.username': 'VHAW050'})
        msg = 'Validate missing username should be False'
        self.assertFalse(received, msg)

        received = self._adp.validate({'agent.postcode': '3000',
                                       'agent.state': 'VIC',
                                       'delivery_partner.id': 1})
        msg = 'Validate missing username/password should be False'
        self.assertFalse(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._adp = None
