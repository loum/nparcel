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
        expected = 'username=%3Cput+your+email_user+name+here%3E&password=%3Cput+your+email_pw+password+here%3E&message=Content-Type%3A+text%2Fplain%3B+charset%3D%22us-ascii%22%5CnMIME-Version%3A+1.0%5CnContent-Transfer-Encoding%3A+7bit%5CnSubject%3A+Test+Message+from+Toll%5CnFrom%3A+loumar%40tollgroup.com%5CnTo%3A+loumar%40tollgroup.com%5Cn%5CnTEST+MESSAGE'
        msg = 'Encoded message not as expected'
        self.assertEqual(received, expected, msg)

    def test_send(self):
        """
        """
        self._re.set_proxy(self._proxy)
        self._re.set_proxy_scheme('https')
        self._re.set_api(self._api)

        received = self._re.send('tester', dry=True)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._re = None
        cls._proxy = None
        cls._api = None
        cls._user = None
        cls._pw = None
