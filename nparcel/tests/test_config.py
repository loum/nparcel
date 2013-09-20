import unittest2

import nparcel


class TestConfig(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/conf/nparceld.conf'

    def setUp(self):
        self._c = nparcel.Config()

    def test_init(self):
        """Initialise a Config object.
        """
        msg = 'Object is not a nparcel.Config'
        self.assertIsInstance(self._c, nparcel.Config, msg)

    def test_parse_config_no_file(self):
        """Read config with no file provided.
        """
        self.assertRaises(SystemExit, self._c.parse_config)

    def test_read_config(self):
        """Read valid config.
        """
        old_config = self._c.config_file
        received = self._c.set_config_file('nparcel/conf/nparceld.conf')
        msg = 'Config should read without error and return None'
        self.assertIsNone(received, msg)

    def test_db_kwargs_no_items(self):
        """Produce a DB connection string -- no items.
        """
        self._c.set_config_file(self._file)

        msg = 'DB connection string should be None'
        self.assertIsNone(self._c.db_kwargs(), msg)

    def tearDown(self):
        self._c = None

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
        expected = {'host': 'auproxy-farm.toll.com.au',
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

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        del cls._file
