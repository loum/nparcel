import unittest2

import nparcel


class TestConfig(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/conf/nparceld.conf'
        cls._c = nparcel.Config()

    def test_init(self):
        """Initialise a Config object.
        """
        msg = 'Object is not a nparcel.Config'
        self.assertIsInstance(self._c, nparcel.Config, msg)

    def test_set_missing_config_file(self):
        """Set missing config file.
        """
        self.assertRaises(SystemExit, self._c.set_file, 'dodgy')

    def test_set_valid_config_file(self):
        """Set a valid config file.
        """
        msg = 'Valid config file assignment should return None'
        self.assertIsNone(self._c.set_file(file=self._file), msg)

        # Cleanup.
        self._c._file = None

    def test_parse_config_no_file(self):
        """Parse items from the config -- no file.
        """
        self.assertRaises(SystemExit, self._c.parse_config)

    def test_parse_config(self):
        """Parse items from the config.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        # Check against expected config items.
        msg = 'Directories to check not as expected'
        received = self._c('in_dirs')
        expected = ['/var/ftp/pub/nparcel/priority/in']
        self.assertListEqual(received, expected, msg)

        msg = 'Archive directory not as expected'
        received = self._c('archive_dir')
        expected = '/data/nparcel/archive'
        self.assertEqual(received, expected, msg)

        msg = 'Signature directory not as expected'
        received = self._c('signature_dir')
        expected = '/data/www/nparcel/data/signature'
        self.assertEqual(received, expected, msg)

        msg = 'Staging base directory not as expected'
        received = self._c('staging_base')
        expected = '/var/ftp/pub/nparcel'
        self.assertEqual(received, expected, msg)

        msg = 'Loader loop not as expected'
        received = self._c('loader_loop')
        expected = 30
        self.assertEqual(received, expected, msg)

        msg = 'Exporter loop not as expected'
        received = self._c('exporter_loop')
        expected = 300
        self.assertEqual(received, expected, msg)

        msg = 'Business units not as expected'
        received = self._c('business_units')
        expected = {'priority': '1', 'fast': '2', 'ipec': '3'}
        self.assertDictEqual(received, expected, msg)

        msg = 'Filename Business units not as expected'
        received = self._c('file_bu')
        expected = {'tolp': '1', 'tolf': '2', 'toli': '3'}
        self.assertDictEqual(received, expected, msg)

        msg = 'Support emails not as expected'
        received = self._c('support_emails')
        expected = ['loumar@tollgroup.com']
        self.assertListEqual(received, expected, msg)

        msg = 'Conditions map not as expected'
        received = self._c('cond')
        expected = {'tolp': '00010',
                    'tolf': '00010',
                    'toli': '10001'}
        self.assertDictEqual(received, expected, msg)

        msg = 'RESTful API not as expected'
        received = self._c('rest')
        expected = {'sms_scheme': 'https',
                    'sms_api': 'https://www.textmagic.com/app/api'}
        self.assertDictEqual(received, expected, msg)

        msg = 'Exporter columns expected'
        received = self._c('exporter_fields')
        expected = {'tolp': '0,1,2,3,4,5',
                    'toli': '0,1,2,3,4,5,6,7'}
        self.assertDictEqual(received, expected, msg)

        # Cleanup.
        self._c._file = None

    def test_db_kwargs_no_items(self):
        """Produce a DB connection string -- no items.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        msg = 'DB connection string should be None'
        self.assertIsNone(self._c.db_kwargs(), msg)

        # Cleanup.
        self._c._file = None

    def test_proxy_kwargs_no_items(self):
        """Produce a proxy connection dictionary structure -- no items.
        """
        self._c._config.remove_section('proxy')
        msg = 'Proxy connection string should return None'
        self.assertIsNone(self._c.proxy_kwargs(), msg)

    def test_proxy_kwargs(self):
        """Produce a proxy connection dictionary structure.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        msg = 'Proxy kwargs should produce a populated dictionary'
        received = self._c.proxy_kwargs()
        expected = {'host': 'auproxy-farm.toll.com.au',
                    'password': '<put your proxy password here>',
                    'port': 8080,
                    'protocol': 'https',
                    'user': 'loumar'}
        self.assertDictEqual(received, expected, msg)

        # Cleanup.
        self._c._file = None

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

    def test_condition_flag_item_excp_true(self):
        """Check item_excp flag settings -- True.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        received = self._c.condition('toli', 'item_number_excp')
        msg = 'Flag value "1" should return True'
        self.assertTrue(received, msg)

        # Cleanup.
        self._c._file = None

    def test_condition_flag_item_excp_false(self):
        """Check item_excp flag settings -- False.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        received = self._c.condition('tolp', 'item_number_excp')
        msg = 'Flag value "0" should return False'
        self.assertFalse(received, msg)

        # Cleanup.
        self._c._file = None

    def test_condition_flag_undefined_flag(self):
        """Check item_excp flag settings -- undefined flag.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        received = self._c.condition('toli', 'banana')
        msg = 'Flag value "banana" should return False'
        self.assertFalse(received, msg)

        # Cleanup.
        self._c._file = None

    def test_condition_flag_undefined_bu(self):
        """Check item_excp flag settings -- undefined BU.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        received = self._c.condition('fruit', 'item_number_excp')
        msg = 'Undefined BU value "fruit" should return False'
        self.assertFalse(received, msg)

        # Cleanup.
        self._c._file = None

    def test_condition_no_conditions(self):
        """Check condition settings -- missing condition.
        """
        received = self._c.condition('fruit', 'item_number_excp')
        msg = 'Missing condition section should return False'
        self.assertFalse(received, msg)

    def test_condition_map_no_bu(self):
        """Check condition map -- missing Business Unit.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        received = self._c.condition_map('banana')
        expected = {'item_number_excp': False,
                    'send_sms': False,
                    'send_email': False,
                    'send_ps_file': False,
                    'send_png_file': False}
        msg = 'Dodgy Business Unit condition map should be empty dict'
        self.assertDictEqual(received, expected, msg)

        # Cleanup.
        self._c._file = None

    def test_condition_map_valid_bu(self):
        """Check condition map -- valid Business Unit.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        received = self._c.condition_map('toli')
        expected = {'item_number_excp': True,
                    'send_sms': False,
                    'send_email': False,
                    'send_ps_file': False,
                    'send_png_file': True}
        msg = 'Valid Business Unit condition map should produce dict values'
        self.assertDictEqual(received, expected, msg)

        # Cleanup.
        self._c._file = None

    def test_required_facility_when_flag_not_set(self):
        """Required facility when a flag is not set.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        msg = 'Facility check should return False if flag is set'
        self.assertFalse(self._c.required_facility('send_sms'), msg)

        # Cleanup.
        self._c._file = None

    def test_required_facility_when_flag_set(self):
        """Required facility when a flag is set.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        old_flag = self._c.cond.get('toli', 'send_sms')
        self._c.cond['toli'] = '10100'

        msg = 'Facility check should return True if flag is set'
        self.assertTrue(self._c.required_facility('send_sms'), msg)

        # Cleanup.
        self._c.cond['toli'] = old_flag
        self._c._file = None

    def test_file_control(self):
        """Check file control dictionary structure.
        """
        self._c.set_file(file=self._file)
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

        # Cleanup.
        self._c._file = None

    def test_bu_to_file(self):
        """Translate business unit name to file name code.
        """
        self._c.set_file(file=self._file)
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

        # Cleanup.
        self._c._file = None

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        cls._c = None
