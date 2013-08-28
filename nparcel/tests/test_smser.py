import unittest2

import nparcel


class TestSmser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._sms = nparcel.Smser()
        conf = nparcel.Config()
        conf.set_file('nparcel/conf/nparceld.conf')
        conf.parse_config()
        cls._proxy = conf.proxy_string()
        cls._api = conf.rest.get('sms_api')

    def test_init(self):
        """Verify initialisation of an nparcel.Emailer object.
        """
        msg = 'Object is not an nparcel.Smser'
        self.assertIsInstance(self._sms, nparcel.Smser, msg)

    def test_send_without_recipients(self):
        """Send message without recipients specified.
        """
        kwargs = {'msg': 'no recipients msg',
                  'dry': True}
        received = self._sms.send(**kwargs)
        msg = 'SMS send without recipients should be (False) True'
        self.assertTrue(received, msg)

        # Clean up.
        self._sms.set_recipients(None)

    def test_generate_url(self):
        """Generate a URL-encoded message.
        """
        sms_msg = """Your consignment has been placed at Skylark News, 59 Skylark Street, INALA 4077. A Consignment Ref 4156736304. Please bring your photo ID with you. Enquiries 13 32 78"""

        received = self._sms.encode_params(sms_msg, mobile='0431602145')
        expected = """username=lubster&text=Your+consignment+has+been+placed+at+Skylark+News%2C+59+Skylark+Street%2C+INALA+4077.+A+Consignment+Ref+4156736304.+Please+bring+your+photo+ID+with+you.+Enquiries+13+32+78&cmd=send&phone=0431602145&unicode=0&password=Nlj3hCb1PdsgoJZ"""
        msg = 'Encoded URL incorrect'
        self.assertEqual(received, expected, msg)

    def test_send(self):
        """Send SMS.
        """
        self._sms.set_proxy(self._proxy)
        self._sms.set_proxy_scheme('https')
        self._sms.set_api(self._api)

        sms_msg = """Your consignment has been placed at Skylark News, 59 Skylark Street, INALA 4077. A Consignment Ref 4156736304. Please bring your photo ID with you. Enquiries 13 32 78"""
        self._sms.set_recipients(['0431602145'])

        received = self._sms.send(sms_msg, dry=True)
        msg = 'SMS send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._sms.set_recipients(None)
        self._sms.set_proxy(None)
        self._sms.set_proxy_scheme('http')
        self._sms.set_api(None)

    def test_mobile_validate(self):
        """Validate mobile number -- valid
        """
        mobile = '0431602145'
        received = self._sms.validate(mobile)
        msg = 'Valid mobile number should validate'
        self.assertTrue(received, msg)

    def test_mobile_validate_not_10_digits(self):
        """Validate mobile number -- not 10 digits.
        """
        msg = 'Mobile number not 10 digits should not validate'

        mobile = '043160214'
        received = self._sms.validate(mobile)
        self.assertFalse(received, msg)

        mobile = '04316021455'
        received = self._sms.validate(mobile)
        self.assertFalse(received, msg)

        mobile = '043160214a'
        received = self._sms.validate(mobile)
        self.assertFalse(received, msg)

    def test_mobile_does_not_start_with_04(self):
        """Validate mobile number -- does not start with 04.
        """
        msg = 'Mobile number does not start with "04" should not validate'

        mobile = 'a431602145'
        received = self._sms.validate(mobile)
        self.assertFalse(received, msg)

        mobile = '0531602145'
        received = self._sms.validate(mobile)
        self.assertFalse(received, msg)

    def test_mobile_empty(self):
        """Validate mobile number -- empty.
        """
        msg = 'Empty mobile number should not validate'

        mobile = ''
        received = self._sms.validate(mobile)
        self.assertFalse(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._sms = None
        cls._proxy = None
        cls._api = None
