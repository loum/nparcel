import unittest2
import string

import nparcel


class TestRestSmser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._rs = nparcel.RestSmser()
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
        self.assertIsInstance(self._rs, nparcel.RestSmser, msg)

    def test_send(self):
        """Send REST SMS.
        """
        self._rs.set_proxy(self._proxy)
        self._rs.set_api(self._api)
        self._rs.set_api_username(self._api_username)
        self._rs.set_api_password(self._api_password)

        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'item_nbr': '1234567890_item_nbr',
             'mobile': '0431602145'}
        f = open('nparcel/templates/sms_xml.t')
        sms_t = f.read()
        f.close()
        sms_s = string.Template(sms_t)
        sms = sms_s.substitute(**d)

        received = self._rs.send(sms, dry=True)
        msg = 'SMS send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._rs.set_proxy(None)
        self._rs.set_api(None)
        self._rs.set_api_username(None)
        self._rs.set_api_password(None)

    def test_mobile_validate(self):
        """Validate mobile number -- valid
        """
        mobile = '0431602145'
        received = self._rs.validate(mobile)
        msg = 'Valid mobile number should validate'
        self.assertTrue(received, msg)

    def test_mobile_validate_not_10_digits(self):
        """Validate mobile number -- not 10 digits.
        """
        msg = 'Mobile number not 10 digits should not validate'

        mobile = '043160214'
        received = self._rs.validate(mobile)
        self.assertFalse(received, msg)

        mobile = '04316021455'
        received = self._rs.validate(mobile)
        self.assertFalse(received, msg)

        mobile = '043160214a'
        received = self._rs.validate(mobile)
        self.assertFalse(received, msg)

    def test_mobile_does_not_start_with_04(self):
        """Validate mobile number -- does not start with 04.
        """
        msg = 'Mobile number does not start with "04" should not validate'

        mobile = 'a431602145'
        received = self._rs.validate(mobile)
        self.assertFalse(received, msg)

        mobile = '0531602145'
        received = self._rs.validate(mobile)
        self.assertFalse(received, msg)

    def test_mobile_empty(self):
        """Validate mobile number -- empty.
        """
        msg = 'Empty mobile number should not validate'

        mobile = ''
        received = self._rs.validate(mobile)
        self.assertFalse(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._rs = None
        del cls._rs
        cls._proxy = None
        del cls._proxy
        cls._api = None
        del cls._api
        cls._api_username = None
        del cls._api_username
        cls._api_proxy = None
        del cls._api_proxy
