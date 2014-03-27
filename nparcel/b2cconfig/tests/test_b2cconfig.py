import unittest2
import datetime
import os

import nparcel


class TestB2CConfig(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = os.path.join('nparcel', 'conf', 'nparceld.conf')

    def setUp(self):
        self._c = nparcel.B2CConfig()

    def test_init(self):
        """Initialise a B2CConfig object.
        """
        msg = 'Object is not a nparcel.B2CConfig'
        self.assertIsInstance(self._c, nparcel.B2CConfig, msg)

    def test_parse_config(self):
        """Parse items from the config.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        msg = 'environment.prod not as expected'
        received = self._c.prod
        expected = 'faswbaup02'
        self.assertEqual(received, expected, msg)

        msg = 'Business units not as expected'
        received = self._c.business_units
        expected = {'priority': 1, 'fast': 2, 'ipec': 3}
        self.assertDictEqual(received, expected, msg)

        msg = 'T1250 file name format not as expected'
        received = self._c.t1250_file_format
        expected = 'T1250_TOL.*\.txt'
        self.assertEqual(received, expected, msg)

        msg = 'Filename Business units not as expected'
        received = self._c.file_bu
        expected = {'tolp': 1,
                    'tolf': 2,
                    'tolf_nsw': 2,
                    'tolf_vic': 2,
                    'tolf_qld': 2,
                    'tolf_sa': 2,
                    'tolf_wa': 2,
                    'tolf_act': 2,
                    'toli': 3}
        self.assertDictEqual(received, expected, msg)

        msg = 'Support emails not as expected'
        received = self._c.support_emails
        expected = ['loumar@tollgroup.com']
        self.assertListEqual(received, expected, msg)

        msg = 'Conditions map not as expected'
        received = self._c.cond
        expected = {'tolp': '000100000000010110',
                    'tolf': '000101100000010110',
                    'toli': '100010000000010110'}
        self.assertDictEqual(received, expected, msg)

        msg = 'RESTful API not as expected'
        received = self._c.rest
        e_scheme = 'https'
        e_uri = 'apps.cinder.co/tollgroup/wsemail/emailservice.svc/sendemail'
        sms_api = 'https://api.esendex.com/v1.0/messagedispatcher'
        expected = {'sms_api': sms_api,
                    'email_api': "%s://%s" % (e_scheme, e_uri),
                    'email_user': '',
                    'email_pw': '',
                    'sms_user': '',
                    'sms_pw': '',
                    'failed_email': 'loumar@tollgroup.com'}
        self.assertDictEqual(received, expected, msg)

        msg = 'Exporter columns expected'
        received = self._c.exporter_fields
        expected = {'tolp': '0,1,2,3,4,5,6',
                    'tolf': '0,1,2,3,4,5,6',
                    'toli': '0,1,2,3,4,5,6,7'}
        self.assertDictEqual(received, expected, msg)

    def test_parse_config_dirs(self):
        """Parse items from the config -- directories ([dirs]).
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()
        # Check against expected config items.
        msg = 'Directories to check not as expected'
        received = self._c.in_dirs
        expected = ['/var/ftp/pub/nparcel/priority/in']
        self.assertListEqual(received, expected, msg)

        msg = 'Archive directory not as expected'
        received = self._c.archive_dir
        expected = '/data/nparcel/archive'
        self.assertEqual(received, expected, msg)

        msg = 'Staging base directory not as expected'
        received = self._c.staging_base
        expected = '/var/ftp/pub/nparcel'
        self.assertEqual(received, expected, msg)

        msg = 'Aggregator directory not as expected'
        received = self._c.aggregator_dirs
        expected = ['/data/nparcel/aggregate']
        self.assertListEqual(received, expected, msg)

        msg = 'ADP directories not as expected'
        received = self._c.adp_dirs
        expected = ['/var/ftp/pub/nparcel/adp/in']
        self.assertListEqual(received, expected, msg)

    def test_parse_config_pe(self):
        """Parse items from the config -- Primary Elect.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        msg = 'Primary Elect file format not as expected'
        received = self._c.pe_in_file_format
        expected = 'T1250_TOL[PIF]_\d{14}\.dat'
        self.assertEqual(received, expected, msg)

        msg = 'Primary Elect archive string not as expected'
        received = self._c.pe_in_file_archive_string
        expected = 'T1250_TOL[PIF]_(\d{8})\d{6}\.dat'
        self.assertEqual(received, expected, msg)

        msg = 'Primary Elect customer not as expected'
        received = self._c.pe_customer
        expected = 'gis'
        self.assertEqual(received, expected, msg)

        msg = 'TCD inbound directory not as expected'
        received = self._c.inbound_tcd
        expected = ['/var/ftp/pub/nparcel/tcd/in']
        self.assertListEqual(received, expected, msg)

        msg = 'TCD filename error'
        received = self._c.tcd_filename_format
        expected = 'TCD_Deliveries_\d{14}\.DAT'
        self.assertEqual(received, expected, msg)

        msg = 'On Delivery uncollected day range error'
        received = self._c.uncollected_day_range
        expected = 14.0
        self.assertEqual(received, expected, msg)

        msg = 'TCD file cache size error'
        received = self._c.file_cache_size
        expected = 5
        self.assertEqual(received, expected, msg)

    def test_parse_config_timeout(self):
        """Parse items from the config -- timeout.
        """
        msg = 'Loader loop not as expected'
        received = self._c.loader_loop
        expected = 30
        self.assertEqual(received, expected, msg)

        msg = 'On delivery loop not as expected'
        received = self._c.ondelivery_loop
        expected = 30
        self.assertEqual(received, expected, msg)

        msg = 'Exporter loop not as expected'
        received = self._c.exporter_loop
        expected = 3600
        self.assertEqual(received, expected, msg)

        msg = 'Mapper loop not as expected'
        received = self._c.mapper_loop
        expected = 30
        self.assertEqual(received, expected, msg)

        msg = 'Filter loop not as expected'
        received = self._c.filter_loop
        expected = 30
        self.assertEqual(received, expected, msg)

        msg = 'ADP loop not as expected'
        received = self._c.adp_loop
        expected = 30
        self.assertEqual(received, expected, msg)

    def test_parse_config_mapper(self):
        """Parse items from the config -- mapper
        """
        msg = 'Mapper inbound dir not as expected'
        received = self._c.mapper_in_dirs
        expected = []
        self.assertListEqual(received, expected, msg)

    def test_parse_config_transsend(self):
        """Parse items from the config -- TransSend.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.delivered_header
        expected = 'latest_scan_event_action'
        msg = 'TransSend delivered_header value error'
        self.assertEqual(received, expected, msg)

        received = self._c.delivered_event_key
        expected = 'delivered'
        msg = 'TransSend delivered_event_key value error'
        self.assertEqual(received, expected, msg)

        received = self._c.scan_desc_header.lower()
        expected = 'latest_scanner_description'
        msg = 'TransSend scan_desc_header value error'
        self.assertEqual(received, expected, msg)

        received = self._c.scan_desc_keys
        expected = ['IDS - TOLL FAST GRAYS ONLINE']
        msg = 'TransSend scan_desc_keys value error'
        self.assertListEqual(received, expected, msg)

    def test_parse_config_filter(self):
        """Parse items from the config -- filter.
        """
        msg = 'Filter customer not as expected'
        received = self._c.filter_customer
        expected = 'parcelpoint'
        self.assertEqual(received, expected, msg)

        msg = 'Filtering rules list not as expected'
        received = self._c.filtering_rules
        expected = ['P', 'R']
        self.assertListEqual(received, expected, msg)

    def test_parse_config_adp(self):
        """Parse items from the config -- adp_headers
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

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
        msg = 'ADP headers not as expected'
        self.assertDictEqual(received, expected, msg)

        received = self._c.adp_file_formats
        expected = []
        msg = 'ADP adp_file_formats value error'
        self.assertListEqual(received, expected, msg)

        received = self._c.code_header
        expected = 'TP Code'
        msg = 'ADP code_header value error'
        self.assertEqual(received, expected, msg)

        received = self._c.delivery_partners
        expected = ['Nparcel', 'ParcelPoint', 'Toll', 'National Storage']
        msg = 'ADP delivery partners error'
        self.assertListEqual(received, expected, msg)

        received = self._c.adp_default_passwords
        expected = {'nparcel': 'aaaa',
                    'parcelpoint': 'bbbb',
                    'toll': 'cccc',
                    'national storage': 'dddd'}
        msg = 'ADP delivery partners default passwords error'
        self.assertDictEqual(received, expected, msg)

    def test_condition_flag_item_excp_true(self):
        """Check item_excp flag settings -- True.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.condition('toli', 'item_number_excp')
        msg = 'Flag value "1" should return True'
        self.assertTrue(received, msg)

    def test_condition_flag_item_excp_false(self):
        """Check item_excp flag settings -- False.
        """
        self._c.set_config_file(self._file)

        received = self._c.condition('tolp', 'item_number_excp')
        msg = 'Flag value "0" should return False'
        self.assertFalse(received, msg)

    def test_condition_flag_undefined_flag(self):
        """Check item_excp flag settings -- undefined flag.
        """
        self._c.set_config_file(self._file)

        received = self._c.condition('toli', 'banana')
        msg = 'Flag value "banana" should return False'
        self.assertFalse(received, msg)

    def test_condition_flag_state_based_reporting(self):
        """Check state_reporting flag settings.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.condition('tolf', 'state_reporting')
        msg = 'Fast "state_reporting" should return True'
        self.assertTrue(received, msg)

        received = self._c.condition('toli', 'state_reporting')
        msg = 'Ipec "state_reporting" should return False'
        self.assertFalse(received, msg)

    def test_condition_flag_undefined_bu(self):
        """Check item_excp flag settings -- undefined BU.
        """
        self._c.set_config_file(self._file)

        received = self._c.condition('fruit', 'item_number_excp')
        msg = 'Undefined BU value "fruit" should return False'
        self.assertFalse(received, msg)

    def test_condition_no_conditions(self):
        """Check condition settings -- missing condition.
        """
        received = self._c.condition('fruit', 'item_number_excp')
        msg = 'Missing condition section should return False'
        self.assertFalse(received, msg)

    def test_condition_map_no_bu(self):
        """Check condition map -- missing Business Unit.
        """
        self._c.set_config_file(self._file)

        received = self._c.condition_map('banana')
        expected = {'item_number_excp': False,
                    'send_sms': False,
                    'send_email': False,
                    'send_ps_file': False,
                    'send_png_file': False,
                    'state_reporting': False,
                    'pe_pods': False,
                    'aggregate_files': False,
                    'send_sc_1': False,
                    'send_sc_2': False,
                    'send_sc_4': False,
                    'delay_template_sc_4': False,
                    'ignore_sc_4': False,
                    'pe_comms': False,
                    'on_del_sc_4': False,
                    'archive_ps_file': False,
                    'archive_png_file': False,
                    'delay_template_sc_2': False}
        msg = 'Dodgy Business Unit condition map should be empty dict'
        self.assertDictEqual(received, expected, msg)

    def test_comms_map(self):
        """Comms map.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.comms_map('toli')
        exepected = {'send_email': False,
                     'send_sms': False}
        msg = 'toli cond_map error'
        self.assertDictEqual(received, exepected, msg)

        old_cond_map = self._c.cond.get('toli')
        cond_map_list = list(old_cond_map)

        cond_map_list[1] = '1'
        self._c.cond['toli'] = ''.join(cond_map_list)
        received = self._c.comms_map('toli')
        exepected = {'send_email': True,
                     'send_sms': False}
        msg = 'toli cond_map error -- send_email True'
        self.assertDictEqual(received, exepected, msg)

        cond_map_list[2] = '1'
        self._c.cond['toli'] = ''.join(cond_map_list)
        received = self._c.comms_map('toli')
        exepected = {'send_email': True,
                     'send_sms': True}
        msg = 'toli cond_map error -- send_sms and send_email True'
        self.assertDictEqual(received, exepected, msg)

        # Clean up.
        self._c.cond['toli'] = old_cond_map

    def test_condition_map_valid_bu(self):
        """Check condition map -- valid Business Unit.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.condition_map('toli')
        expected = {'item_number_excp': True,
                    'send_sms': False,
                    'send_email': False,
                    'send_ps_file': False,
                    'send_png_file': True,
                    'state_reporting': False,
                    'pe_pods': False,
                    'aggregate_files': False,
                    'send_sc_1': False,
                    'send_sc_2': False,
                    'send_sc_4': False,
                    'delay_template_sc_4': False,
                    'ignore_sc_4': False,
                    'pe_comms': True,
                    'on_del_sc_4': False,
                    'archive_ps_file': True,
                    'archive_png_file': True,
                    'delay_template_sc_2': False}
        msg = 'Valid Business Unit condition map should produce dict values'
        self.assertDictEqual(received, expected, msg)

    def test_condition_map_tolf(self):
        """Check condition map -- Fast state based BU.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.condition_map('tolf_nsw')
        expected = {'item_number_excp': False,
                    'send_sms': False,
                    'send_email': False,
                    'send_ps_file': True,
                    'send_png_file': False,
                    'state_reporting': True,
                    'pe_pods': True,
                    'aggregate_files': False,
                    'send_sc_1': False,
                    'send_sc_2': False,
                    'send_sc_4': False,
                    'delay_template_sc_4': False,
                    'ignore_sc_4': False,
                    'pe_comms': True,
                    'on_del_sc_4': False,
                    'archive_ps_file': True,
                    'archive_png_file': True,
                    'delay_template_sc_2': False}
        msg = 'Fast condition map should produce dict values'
        self.assertDictEqual(received, expected, msg)

    def test_required_facility_when_flag_not_set(self):
        """Required facility when a flag is not set.
        """
        self._c.set_config_file(self._file)

        msg = 'Facility check should return False if flag is set'
        self.assertFalse(self._c.required_facility('send_sms'), msg)

    def test_required_facility_when_flag_set(self):
        """Required facility when a flag is set.
        """
        self._c.set_config_file(self._file)

        old_flag = self._c.cond.get('toli', 'send_sms')
        self._c.cond['toli'] = '10100'

        msg = 'Facility check should return True if flag is set'
        self.assertTrue(self._c.required_facility('send_sms'), msg)

    def test_file_control(self):
        """Check file control dictionary structure.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.get_pod_control('tolp')
        expected = {'ps': True, 'png': False}
        msg = 'Priority file control dictionary not as expected'
        self.assertDictEqual(received, expected, msg)

        received = self._c.get_pod_control('toli')
        expected = {'ps': False, 'png': True}
        msg = 'Ipec file control dictionary not as expected'
        self.assertDictEqual(received, expected, msg)

        received = self._c.get_pod_control('bogus')
        expected = {'ps': False, 'png': False}
        msg = 'Bogus file control dictionary not as expected'
        self.assertDictEqual(received, expected, msg)

    def test_bu_to_file(self):
        """Translate business unit name to file name code.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.bu_to_file(1)
        expected = 'tolp'
        msg = 'Priority bu_to_file translation not as expected'
        self.assertEqual(received, expected, msg)

        received = self._c.bu_to_file(2)
        expected = 'tolf'
        msg = 'Fast bu_to_file translation not as expected'
        self.assertEqual(received, expected, msg)

        received = self._c.bu_to_file(3)
        expected = 'toli'
        msg = 'Ipec bu_to_file translation not as expected'
        self.assertEqual(received, expected, msg)

        received = self._c.bu_to_file('dodgy')
        msg = 'Dodgy bu_to_file translation not None'
        self.assertIsNone(received, msg)

    def test_bu_ids_with_set_condition(self):
        """Check Business Unit IDs that are set in the condition map.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.bu_ids_with_set_condition('pe_comms')
        expected = (1, 2, 3)
        msg = 'pe_comms set condition map BU ids error'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.bu_ids_with_set_condition('item_number_excp')
        expected = (3,)
        msg = 'item_number_excp set condition map BU ids error'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.bu_ids_with_set_condition('on_del_sc_4')
        expected = ()
        msg = 'on_del_sc_4 set condition map BU ids error'
        self.assertTupleEqual(received, expected, msg)

    def test_db_kwargs_no_items(self):
        """Produce a DB connection string -- no items.
        """
        self._c.set_config_file(self._file)

        msg = 'DB connection string should be None'
        self.assertIsNone(self._c.db_kwargs(), msg)

    def test_ts_db_kwargs_no_items(self):
        """Produce a TransSend DB connection string -- no items.
        """
        self._c.set_config_file(self._file)

        msg = 'TransSend DB connection string should be None'
        self.assertIsNone(self._c.ts_db_kwargs(), msg)

    def test_proxy_kwargs_no_items(self):
        """Produce a proxy connection dictionary structure -- no items.
        """
        msg = 'Proxy connection string should return None'
        self.assertIsNone(self._c.proxy_kwargs(), msg)

    def test_proxy_kwargs(self):
        """Produce a proxy connection dictionary structure.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        msg = 'Proxy kwargs should produce a populated dictionary'
        received = self._c.proxy_kwargs()
        expected = None
        if received is not None:
            expected = {'host': 'auproxy-farm.toll.com.au',
                        'password': '',
                        'port': 8080,
                        'protocol': 'https',
                        'user': 'loumar'}
        self.assertEqual(received, expected, msg)

    def test_proxy_string_no_values(self):
        """Produce a proxy string -- no values.
        """
        msg = 'Proxy string with no kwargs should return None'
        self.assertIsNone(self._c.proxy_string(), msg)

    def test_proxy_string(self):
        """Produce a proxy string.
        """
        kwargs = {'host': 'auproxy-farm.toll.com.au',
                  'user': 'loumar',
                  'password': 'pw',
                  'port': '8080'}
        msg = 'Proxy string generation incorrect'
        received = self._c.proxy_string(kwargs)
        expected = 'loumar:pw@auproxy-farm.toll.com.au:8080'
        self.assertEqual(received, expected, msg)

    def test_sms_api_kwargs(self):
        """Produce a REST SMS API dictionary structure.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        msg = 'SMS API kwargs should produce a populated dictionary'
        received = self._c.sms_api_kwargs
        expected = {'api': 'https://api.esendex.com/v1.0/messagedispatcher',
                    'api_username': '',
                    'api_password': ''}
        self.assertDictEqual(received, expected, msg)

    def test_email_api_kwargs(self):
        """Produce a REST email API dictionary structure.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        msg = 'Email API kwargs should produce a populated dictionary'
        received = self._c.email_api_kwargs
        scheme = 'https'
        url = 'apps.cinder.co/tollgroup/wsemail/emailservice.svc/sendemail'
        api = '%s://%s' % (scheme, url)
        expected = {'api': api,
                    'api_username': '',
                    'api_password': '',
                    'support': 'loumar@tollgroup.com'}
        self.assertDictEqual(received, expected, msg)

    def tearDown(self):
        self._c = None
        del self._c

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        del cls._file
