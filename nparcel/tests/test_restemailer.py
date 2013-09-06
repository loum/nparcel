import unittest2

import nparcel


class TestRestEmailer(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._re = nparcel.RestEmailer()
        conf = nparcel.Config()
        conf.set_file('nparcel/conf/nparceld.conf')
        conf.parse_config()
        cls._proxy = conf.proxy_string()
        cls._api = conf.rest.get('email_api')
        cls._user = conf.rest.get('email_user')
        cls._pw = conf.rest.get('email_pw')

    def test_init(self):
        """Verify initialisation of an nparcel.RestEmailer object.
        """
        msg = 'Object is not an nparcel.RestEmailer'
        self.assertIsInstance(self._re, nparcel.RestEmailer, msg)

    def test_encode_params(self):
        """Generate a URL-encoded message.
        """
        subject = 'Test Message from Toll'
        sender = 'loumar@tollgroup.com'
        recipient = 'loumar@tollgroup.com'
        msg = 'TEST MESSAGE'
        received = self._re.encode_params(subject=subject,
                                          username=self._user,
                                          passwd=self._pw,
                                          sender=sender,
                                          recipient=recipient,
                                          msg=msg)
        expected = ''
        msg = 'Encoded message not as expected'
        self.assertEqual(received, expected, msg)

    def test_send(self):
        """
        """
        self._re.set_proxy(self._proxy)
        self._re.set_proxy_scheme('https')
        self._re.set_api(self._api)

        received = self._re.send()
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._re = None
        cls._proxy = None
        cls._api = None
        cls._user = None
        cls._pw = None
