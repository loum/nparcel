import unittest2
import string

import nparcel


class TestRestSmser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._rsms = nparcel.RestSmser()
        conf = nparcel.Config()
        conf.set_file('nparcel/conf/nparceld.conf')
        conf.parse_config()
        cls._proxy = conf.proxy_string()
        cls._api = conf.rest.get('sms_api')
        cls._api_username = conf.rest.get('sms_user')
        cls._api_password = conf.rest.get('sms_pw')

    def test_init(self):
        """Verify initialisation of an nparcel.Emailer object.
        """
        msg = 'Object is not an nparcel.RestSmser'
        self.assertIsInstance(self._rsms, nparcel.RestSmser, msg)

    def test_send(self):
        """Send REST SMS.
        """
        self._rsms.set_proxy(self._proxy)
        self._rsms.set_proxy_scheme('https')
        self._rsms.set_api(self._api)
        self._rsms.set_api_username(self._api_username)
        self._rsms.set_api_password(self._api_password)

        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'item_nbr': '1234567890_item_nbr',
             'mobile': '0431602145'}
        sms = self._rsms.create_comms(data=d, base_dir='nparcel')

        received = self._rsms.send(sms, dry=True)
        msg = 'SMS send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._rsms.set_proxy(None)
        self._rsms.set_proxy_scheme('http')
        self._rsms.set_api(None)
        self._rsms.set_api_username(None)
        self._rsms.set_api_password(None)

    def test_mobile_validate(self):
        """Validate mobile number -- valid
        """
        mobile = '0431602145'
        received = self._rsms.validate(mobile)
        msg = 'Valid mobile number should validate'
        self.assertTrue(received, msg)

    def test_mobile_validate_not_10_digits(self):
        """Validate mobile number -- not 10 digits.
        """
        msg = 'Mobile number not 10 digits should not validate'

        mobile = '043160214'
        received = self._rsms.validate(mobile)
        self.assertFalse(received, msg)

        mobile = '04316021455'
        received = self._rsms.validate(mobile)
        self.assertFalse(received, msg)

        mobile = '043160214a'
        received = self._rsms.validate(mobile)
        self.assertFalse(received, msg)

    def test_mobile_does_not_start_with_04(self):
        """Validate mobile number -- does not start with 04.
        """
        msg = 'Mobile number does not start with "04" should not validate'

        mobile = 'a431602145'
        received = self._rsms.validate(mobile)
        self.assertFalse(received, msg)

        mobile = '0531602145'
        received = self._rsms.validate(mobile)
        self.assertFalse(received, msg)

    def test_mobile_empty(self):
        """Validate mobile number -- empty.
        """
        msg = 'Empty mobile number should not validate'

        mobile = ''
        received = self._rsms.validate(mobile)
        self.assertFalse(received, msg)

    def test_create_comms_missing_xml_input_file(self):
        """Create SMS comms with missing XML input file.
        """
        msg = 'SMS comms string should be None on XML input file error'

        d = {}
        received = self._rsms.create_comms(data=d, base_dir='banana')
        self.assertIsNone(received, msg)

    def test_create_comms_valid_data_structure(self):
        """Create SMS comms with valid data structure.
        """
        msg = 'SMS comms string should be None on XML input file error'

        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'item_nbr': '1234567890_item_nbr',
             'mobile': '0419368910'}
        received = self._rsms.create_comms(data=d, base_dir='nparcel')

        f = open('nparcel/tests/create_comms_valid_data_structure.out')
        expected = f.read().rstrip().replace('\\n', '\n')
        f.close()
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._rsms = None
        del cls._rsms
        cls._proxy = None
        del cls._proxy
        cls._api = None
        del cls._api
        cls._api_username = None
        del cls._api_username
        cls._api_proxy = None
        del cls._api_proxy