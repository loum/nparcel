import unittest2
import datetime

import nparcel


class TestB2CConfig(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/conf/nparceld.conf'

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

        # Check against expected config items.
        msg = 'Directories to check not as expected'
        received = self._c.in_dirs
        expected = ['/var/ftp/pub/nparcel/priority/in']
        self.assertListEqual(received, expected, msg)

        msg = 'Directories to check not as expected'
        received = self._c.pe_in_dirs
        expected = ['/var/ftp/pub/nparcel/gis/in']
        self.assertListEqual(received, expected, msg)

        msg = 'Archive directory not as expected'
        received = self._c.archive_dir
        expected = '/data/nparcel/archive'
        self.assertEqual(received, expected, msg)

        msg = 'Staging base directory not as expected'
        received = self._c.staging_base
        expected = '/var/ftp/pub/nparcel'
        self.assertEqual(received, expected, msg)

        msg = 'Signature directory not as expected'
        received = self._c.signature_dir
        expected = '/data/www/nparcel/data/signature'
        self.assertEqual(received, expected, msg)

        msg = 'Comms directory not as expected'
        received = self._c.comms_dir
        expected = '/data/nparcel/comms'
        self.assertEqual(received, expected, msg)

        msg = 'Loader loop not as expected'
        received = self._c.loader_loop
        expected = 30
        self.assertEqual(received, expected, msg)

        msg = 'Primary elect loop not as expected'
        received = self._c.pe_loop
        expected = 30
        self.assertEqual(received, expected, msg)

        msg = 'Reminder loop not as expected'
        received = self._c.reminder_loop
        expected = 3600
        self.assertEqual(received, expected, msg)

        msg = 'Notifications loop not as expected'
        received = self._c.comms_loop
        expected = 30
        self.assertEqual(received, expected, msg)

        msg = 'Exporter loop not as expected'
        received = self._c.exporter_loop
        expected = 300
        self.assertEqual(received, expected, msg)

        msg = 'Business units not as expected'
        received = self._c.business_units
        expected = {'priority': '1', 'fast': '2', 'ipec': '3'}
        self.assertDictEqual(received, expected, msg)

        msg = 'Filename Business units not as expected'
        received = self._c.file_bu
        expected = {'tolp': '1',
                    'tolf': '2',
                    'tolf_nsw': '2',
                    'tolf_vic': '2',
                    'tolf_qld': '2',
                    'tolf_sa': '2',
                    'tolf_wa': '2',
                    'tolf_act': '2',
                    'toli': '3'}
        self.assertDictEqual(received, expected, msg)

        msg = 'Support emails not as expected'
        received = self._c.support_emails
        expected = ['loumar@tollgroup.com']
        self.assertListEqual(received, expected, msg)

        msg = 'Conditions map not as expected'
        received = self._c.cond
        expected = {'tolp': '000100',
                    'tolf': '000101',
                    'toli': '100010'}
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

        # Reminders.
        received = self._c.notification_delay
        expected = 345600
        msg = 'Reminder notification_delay error'
        self.assertEqual(received, expected, msg)

        received = self._c.start_date
        expected = datetime.datetime(2013, 9, 10, 0, 0, 0)
        msg = 'Reminder start_date error'
        self.assertEqual(received, expected, msg)

        received = self._c.hold_period
        expected = 691200
        msg = 'Comms hold_period error'
        self.assertEqual(received, expected, msg)

        received = self._c.skip_days
        expected = ['Sunday']
        msg = 'Comms skip_days error'
        self.assertListEqual(received, expected, msg)

        received = self._c.send_time_ranges
        expected = ['08:00-19:00']
        msg = 'Comms send_time_ranges error'
        self.assertListEqual(received, expected, msg)

        received = self._c.comms_q_warning
        expected = 100
        msg = 'Comms message queue warning error'
        self.assertEqual(received, expected, msg)

        received = self._c.comms_q_error
        expected = 1000
        msg = 'Comms message queue error error'
        self.assertEqual(received, expected, msg)

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
                    'state_reporting': False}
        msg = 'Dodgy Business Unit condition map should be empty dict'
        self.assertDictEqual(received, expected, msg)

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
                    'state_reporting': False}
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
                    'state_reporting': True}
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

        received = self._c.get_file_control('tolp')
        expected = {'ps': True, 'png': False}
        msg = 'Priority file control dictionary not as expected'
        self.assertDictEqual(received, expected, msg)

        received = self._c.get_file_control('toli')
        expected = {'ps': False, 'png': True}
        msg = 'Ipec file control dictionary not as expected'
        self.assertDictEqual(received, expected, msg)

        received = self._c.get_file_control('bogus')
        expected = {'ps': False, 'png': False}
        msg = 'Bogus file control dictionary not as expected'
        self.assertDictEqual(received, expected, msg)

    def test_bu_to_file(self):
        """Translate business unit name to file name code.
        """
        self._c.set_config_file(self._file)
        self._c.parse_config()

        received = self._c.bu_to_file('priority')
        expected = 'tolp'
        msg = 'Priority bu_to_file translation not as expected'
        self.assertEqual(received, expected, msg)

        received = self._c.bu_to_file('fast')
        expected = 'tolf'
        msg = 'Fast bu_to_file translation not as expected'
        self.assertEqual(received, expected, msg)

        received = self._c.bu_to_file('ipec')
        expected = 'toli'
        msg = 'Ipec bu_to_file translation not as expected'
        self.assertEqual(received, expected, msg)

        received = self._c.bu_to_file('dodgy')
        msg = 'Dodgy bu_to_file translation not None'
        self.assertIsNone(received, msg)

    def test_db_kwargs_no_items(self):
        """Produce a DB connection string -- no items.
        """
        self._c.set_config_file(self._file)

        msg = 'DB connection string should be None'
        self.assertIsNone(self._c.db_kwargs(), msg)

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
        expected = {'host': 'itproxy-farm.toll.com.au',
                    'password': '',
                    'port': 8080,
                    'protocol': 'https',
                    'user': 'loumar'}
        self.assertDictEqual(received, expected, msg)

    def test_proxy_string_no_values(self):
        """Produce a proxy string -- no values.
        """
        msg = 'Proxy string with no kwargs should return None'
        self.assertIsNone(self._c.proxy_string(), msg)

    def test_proxy_string(self):
        """Produce a proxy string.
        """
        kwargs = {'host': 'itproxy-farm.toll.com.au',
                  'user': 'loumar',
                  'password': 'pw',
                  'port': '8080'}
        msg = 'Proxy string generation incorrect'
        received = self._c.proxy_string(kwargs)
        expected = 'loumar:pw@itproxy-farm.toll.com.au:8080'
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
