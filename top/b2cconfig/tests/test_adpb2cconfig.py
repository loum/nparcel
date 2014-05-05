import unittest2
import os

import top


class TestAdpB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = top.AdpB2CConfig()

    def test_init(self):
        """Initialise a AdpB2CConfig object.
        """
        msg = 'Object is not a top.AdpB2CConfig'
        self.assertIsInstance(self._c, top.AdpB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('top', 'conf', 'top.conf')

        self._c.set_config_file(config_file)
        self._c.parse_config()

        received = self._c.adp_loop
        expected = 30
        msg = 'AdpB2CConfig.adp_loop error'
        self.assertEqual(received, expected, msg)

        received = self._c.adp_dirs
        expected = ['/var/ftp/pub/nparcel/adp/in']
        msg = 'AdpB2CConfig.adp_dirs error'
        self.assertListEqual(received, expected, msg)

        received = self._c.archive_dir
        expected = '/data/top/archive'
        msg = 'AdpB2CConfig.archive_dir error'
        self.assertEqual(received, expected, msg)

        received = self._c.adp_file_formats
        expected = []
        msg = 'AdpB2CConfig.adp_file_formats error'
        self.assertListEqual(received, expected, msg)

        # For the default configuration file the [db] section is blank
        received = self._c.db_kwargs()
        msg = 'AdpB2CConfig.db_kwargs error'
        self.assertIsNone(received, msg)

        received = self._c.code_header
        expected = 'TP Code'
        msg = 'AdpB2CConfig.code_header error'
        self.assertEqual(received, expected, msg)

        received = self._c.adp_headers
        expected = {'agent.code': 'TP Code',
                    'agent.dp_code': 'DP Code',
                    'agent.name': 'ADP Name',
                    'agent.address': 'Address',
                    'agent.suburb': 'Suburb',
                    'agent.state': 'State',
                    'agent.postcode': 'Postcode',
                    'agent.opening_hours': 'Opening Hours',
                    'agent.notes': 'Notes',
                    'agent.parcel_size_code': 'ADP Accepts Parcel Size',
                    'agent.phone_nbr': 'Phone',
                    'agent.contact_name': 'Contact',
                    'agent.email': 'Email',
                    'agent.fax_nbr': 'Fax',
                    'agent.status': 'Active',
                    'delivery_partner.id': 'DP Id',
                    'login_account.username': 'Username'}
        msg = 'AdpB2CConfig.adp.headers error'
        self.assertDictEqual(received, expected, msg)

        received = self._c.delivery_partners
        expected = ['Nparcel', 'ParcelPoint', 'Toll', 'National Storage']
        msg = 'AdpB2CConfig.adp.delivery_partners error'
        self.assertListEqual(received, expected, msg)

        received = self._c.adp_default_passwords
        expected = {'nparcel': 'aaaa',
                    'parcelpoint': 'bbbb',
                    'toll': 'cccc',
                    'national storage': 'dddd'}
        msg = 'AdpB2CConfig.adp_default_passwords error'
        self.assertDictEqual(received, expected, msg)

    def tearDown(self):
        del self._c
