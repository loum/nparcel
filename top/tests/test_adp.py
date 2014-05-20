import unittest2
import os
import tempfile

import top
from top.utils.files import (remove_files,
                             copy_file,
                             get_directory_files_list)


class TestAdp(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._adp = top.Adp()

        fixture_dir = os.path.join('top', 'tests', 'fixtures')

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
        msg = 'Object is not a top.Adp'
        self.assertIsInstance(self._adp, top.Adp, msg)

    def test_process_dry_run(self):
        """Check processing -- dry run.
        """
        dry = True

        test_dir = os.path.join('top', 'tests', 'files')
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
        received = self._adp.process(code='V0101', values=code['V010'])
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

    def test_sanitise(self):
        """Sanitise the ADP data.
        """
        received = self._adp.sanitise({'banana': 'YES'})
        expected = {'banana': 'YES',
                    'agent.parcel_size_code': 'S',
                    'login_account.status': 1}
        msg = 'Sanitise status not defined error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'banana': 'YES'})
        expected = {'banana': 'YES',
                    'agent.parcel_size_code': 'S',
                    'login_account.status': 1}
        msg = 'Sanitise status not defined error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'agent.parcel_size_code': 'S'})
        expected = {'agent.parcel_size_code': 'S',
                    'login_account.status': 1}
        msg = 'Sanitise agent.parcel_size_code "S" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'agent.parcel_size_code': 'L'})
        expected = {'agent.parcel_size_code': 'L',
                    'login_account.status': 1}
        msg = 'Sanitise agent.parcel_size_code "L" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'agent.parcel_size_code': 'x'})
        expected = {'agent.parcel_size_code': 'S',
                    'login_account.status': 1}
        msg = 'Sanitise agent.parcel_size_code unknown value error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({})
        expected = {'agent.parcel_size_code': 'S',
                    'login_account.status': 1}
        msg = 'Sanitise agent.parcel_size_code not defined value error'
        self.assertEqual(received, expected, msg)

    def test_sanitise_delivery_partner(self):
        """Sanitise ADP data structure with delivery_partner.id adjustments.
        """
        old_delivery_partners = self._adp.delivery_partners

        self._adp.set_delivery_partners(['Nparcel',
                                         'ParcelPoint',
                                         'Toll',
                                         'National Storage'])
        vals = {'delivery_partner.id': 'Nparcel'}
        received = self._adp.sanitise(vals)
        expected = {'delivery_partner.id': 1,
                    'agent.parcel_size_code': 'S',
                    'login_account.status': 1,
                    'agent.dp_id': 1}
        msg = 'Sanitise delivery_partner "Nparcel" error'
        self.assertDictEqual(received, expected, msg)

        # Unknown delivery partner.
        received = self._adp.sanitise({'delivery_partner.id': 'banana'})
        expected = {'login_account.status': 1,
                    'agent.parcel_size_code': 'S'}
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
                    'agent.parcel_size_code': 'S',
                    'login_account.password': 'aaaa',
                    'login_account.status': 1,
                    'agent.dp_id': 1}
        msg = 'Sanitise password error'
        self.assertDictEqual(received, expected, msg)

        received = self._adp.sanitise({'delivery_partner.id': 'banana'})
        expected = {'login_account.status': 1,
                    'agent.parcel_size_code': 'S'}
        msg = 'Sanitise missing password error'
        self.assertDictEqual(received, expected, msg)

        # Clean up.
        self._adp.set_delivery_partners(old_delivery_partners)
        self._adp.set_default_passwords(old_default_passwords)

    def test_sanitise_login_account_status(self):
        """Sanitise the "login_account.status" column.
        """
        received = self._adp.sanitise({'login_account.status': 'YES'})
        expected = {'login_account.status': 1,
                    'agent.parcel_size_code': 'S'}
        msg = 'Sanitise login_account.status "YES" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'login_account.status': 'Y'})
        expected = {'login_account.status': 1,
                    'agent.parcel_size_code': 'S'}
        msg = 'Sanitise login_account.status "Y" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'login_account.status': 'NO'})
        expected = {'login_account.status': 0,
                    'agent.parcel_size_code': 'S'}
        msg = 'Sanitise login_account.status "NO" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({'login_account.status': 'N'})
        expected = {'login_account.status': 0,
                    'agent.parcel_size_code': 'S'}
        msg = 'Sanitise login_account.status "N" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise({})
        expected = {'login_account.status': 1,
                    'agent.parcel_size_code': 'S'}
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

    def test_update(self):
        """Bulk ADP update.
        """
        code = {}
        code['V010'] = {'agent.code': 'V010',
                        'agent.dp_code': 'VCLA005',
                        'agent.name': None,
                        'agent.address': '',
                        'agent.suburb': 'CLAYTON',
                        'agent.state': 'VIC',
                        'agent.postcode': '3168',
                        'agent.status': 'no',
                        'agent.parcel_size_code': 's',
                        'delivery_partner.dp_id': 'Nparcel',
                        'login_account.username': 'VCLA005'}
        received = self._adp.update(code='V0101', values=code['V010'])
        msg = 'ADP update should return True'
        self.assertTrue(received, msg)

    def test_sanitise_agent_status(self):
        """Sanitise agent status.
        """
        received = self._adp.sanitise_agent_status('1')
        expected = 1
        msg = 'Sanitise agent.status "1" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_status('NO')
        expected = 0
        msg = 'Sanitise agent.status "NO" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_status('YES')
        expected = 1
        msg = 'Sanitise agent.status "YES" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_status('no')
        expected = 0
        msg = 'Sanitise agent.status "no" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_status('yes')
        expected = 1
        msg = 'Sanitise agent.status "yes" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_status('inactive')
        expected = 0
        msg = 'Sanitise agent.status "inactive" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_status('active')
        expected = 1
        msg = 'Sanitise agent.status "active" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_status(None)
        msg = 'Sanitise agent.status None error'
        self.assertIsNone(received, msg)

    def test_sanitise_agent_parcel_size_code(self):
        """Sanitise agent parcel size code.
        """
        received = self._adp.sanitise_agent_parcel_size_code('S')
        expected = 'S'
        msg = 'Sanitise agent.parcel_size_code "S" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_parcel_size_code('L')
        expected = 'L'
        msg = 'Sanitise agent.parcel_size_code "L" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_parcel_size_code('l')
        expected = 'L'
        msg = 'Sanitise agent.parcel_size_code "l" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_parcel_size_code('x')
        expected = 'S'
        msg = 'Sanitise agent.parcel_size_code "x" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_parcel_size_code(None)
        expected = 'S'
        msg = 'Sanitise agent.parcel_size_code None error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_agent_parcel_size_code('')
        expected = 'S'
        msg = 'Sanitise agent.parcel_size_code "" error'
        self.assertEqual(received, expected, msg)

    def test_filter_update_fields(self):
        """Filter the fields to update.
        """
        values = {'agent.code': 'V010',
                  'agent.dp_code': 'VCLA005',
                  'agent.name': 'Clayton Newsagency',
                  'agent.address': '345 Clayton Road',
                  'agent.suburb': 'CLAYTON',
                  'agent.state': 'VIC',
                  'agent.postcode': '3168',
                  'delivery_partner.id': 'Nparcel',
                  'login_account.username': 'VCLA005'}
        received = self._adp.filter_update_fields(values)
        expected = {'agent.code': 'V010',
                    'agent.dp_code': 'VCLA005',
                    'agent.name': 'Clayton Newsagency',
                    'agent.address': '345 Clayton Road',
                    'agent.suburb': 'CLAYTON',
                    'agent.state': 'VIC',
                    'agent.postcode': '3168',
                    'delivery_partner.id': 'Nparcel',
                    'login_account.username': 'VCLA005'}
        msg = 'Filtered fields to update error'
        self.assertDictEqual(received, expected, msg)

    def test_filter_update_fields_set_key(self):
        """Filter the fields to update -- set key value.
        """
        values = {'agent.code': 'V010',
                  'agent.dp_code': 'VCLA005',
                  'agent.name': 'Clayton Newsagency',
                  'agent.address': '345 Clayton Road',
                  'agent.suburb': 'CLAYTON',
                  'agent.state': 'VIC',
                  'agent.postcode': '3168',
                  'delivery_partner.id': 'Nparcel',
                  'login_account.username': 'VCLA005'}
        received = self._adp.filter_update_fields(values, key='agent')
        expected = {'agent.code': 'V010',
                    'agent.dp_code': 'VCLA005',
                    'agent.name': 'Clayton Newsagency',
                    'agent.address': '345 Clayton Road',
                    'agent.suburb': 'CLAYTON',
                    'agent.state': 'VIC',
                    'agent.postcode': '3168'}
        msg = 'Filtered fields to update error - agent key value'
        self.assertDictEqual(received, expected, msg)

    def test_filter_blank_update_fields(self):
        """Filter the blank fields to update.
        """
        values = {'agent.code': 'V010',
                  'agent.dp_code': 'VCLA005',
                  'ADP Name': '',
                  'agent.address': None,
                  'agent.suburb': 'CLAYTON',
                  'agent.state': 'VIC',
                  'agent.sostcode': '3168',
                  'delivery_partner.id': 'Nparcel',
                  'login_account.username': 'VCLA005'}
        received = self._adp.filter_update_fields(values)
        expected = {'agent.code': 'V010',
                    'agent.dp_code': 'VCLA005',
                    'agent.suburb': 'CLAYTON',
                    'agent.state': 'VIC',
                    'agent.sostcode': '3168',
                    'delivery_partner.id': 'Nparcel',
                    'login_account.username': 'VCLA005'}
        msg = 'Filtered blank fields to update error'
        self.assertDictEqual(received, expected, msg)

    def test_filter_blank_update_fields_set_key(self):
        """Filter the blank fields to update -- set key value.
        """
        values = {'agent.code': 'V010',
                  'agent.dp_code': 'VCLA005',
                  'ADP Name': '',
                  'agent.address': None,
                  'agent.suburb': 'CLAYTON',
                  'agent.state': 'VIC',
                  'agent.sostcode': '3168',
                  'delivery_partner.id': 'Nparcel',
                  'login_account.username': 'VCLA005'}
        received = self._adp.filter_update_fields(values, key='agent')
        expected = {'agent.code': 'V010',
                    'agent.dp_code': 'VCLA005',
                    'agent.suburb': 'CLAYTON',
                    'agent.state': 'VIC',
                    'agent.sostcode': '3168'}
        msg = 'Filtered blank fields to update error'
        self.assertDictEqual(received, expected, msg)

    def test_sanitise_delivery_partner_id(self):
        """Sanitise the "delivery_partner.id" column.
        """
        old_delivery_partners = self._adp.delivery_partners

        self._adp.set_delivery_partners(['Nparcel',
                                         'ParcelPoint',
                                         'Toll',
                                         'National Storage'])
        received = self._adp.sanitise_delivery_partner_id('Nparcel')
        expected = 1
        msg = 'Sanitise delivery_partner "Nparcel" error'
        self.assertEqual(received, expected, msg)

        # Unknown delivery partner.
        received = self._adp.sanitise_delivery_partner_id('banana')
        self.assertIsNone(received, msg)

        # Clean up.
        self._adp.set_delivery_partners(old_delivery_partners)

    def test_sanitise_login_account_status(self):
        """Sanitise login account status.
        """
        received = self._adp.sanitise_login_account_status('No')
        expected = 0
        msg = 'Sanitise login_account.status "No" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_login_account_status('Yes')
        expected = 1
        msg = 'Sanitise login_account.status "Yes" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_login_account_status('inactive')
        expected = 0
        msg = 'Sanitise login_account.status "inactive" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_login_account_status('ACTIVE')
        expected = 1
        msg = 'Sanitise login_account.status "ACTIVE" error'
        self.assertEqual(received, expected, msg)

        received = self._adp.sanitise_login_account_status(None)
        expected = 1
        msg = 'Sanitise login_account.status None error'
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._adp = None
