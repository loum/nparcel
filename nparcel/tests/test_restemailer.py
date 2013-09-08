import unittest2

import nparcel


class TestRestEmailer(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._re = nparcel.RestEmailer()

        conf = nparcel.Config()
        conf.set_file('nparcel/conf/nparceld.conf')
        conf.parse_config()
        cls._re.set_proxy(conf.proxy_string())
        cls._re.set_api(conf.rest.get('email_api'))
        cls._re.set_api_username(conf.rest.get('email_user'))
        cls._re.set_api_password(conf.rest.get('email_pw'))

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
                                          sender=sender,
                                          recipient=recipient,
                                          msg=msg)
        expected = 'username=&password=&message=Content-Type%3A+text%2Fplain%3B+charset%3D%22us-ascii%22%5CnMIME-Version%3A+1.0%5CnContent-Transfer-Encoding%3A+7bit%5CnSubject%3A+Test+Message+from+Toll%5CnFrom%3A+loumar%40tollgroup.com%5CnTo%3A+loumar%40tollgroup.com%5Cn%5CnTEST+MESSAGE'
        msg = 'Encoded message not as expected'
        self.assertEqual(received, expected, msg)

    def test_send(self):
        """Send an email message to the REST-based interface.
        """
        subject = 'Test Message from Toll'
        sender = 'loumar@tollgroup.com'
        recipient = 'loumar@tollgroup.com'
        msg = 'TEST MESSAGE'

        received = self._re.send(subject=subject,
                                 sender=sender,
                                 recipient=recipient,
                                 msg=msg,
                                 dry=True)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

    def test_xxx(self):
        """Send an email message to the REST-based interface.
        """
        self._re.set_recipients(['loumar@tollgroup.com'])
        subject = 'Test Message from Toll'
        msg = 'Test message to restful interface'
        received = self._re.xxx(subject=subject,
                                msg=msg,
                                dry=True)

        msg = 'Email send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._re.set_recipients(None)

    @classmethod
    def tearDownClass(cls):
        cls._re = None
        cls._proxy = None
        cls._api = None
        cls._user = None
        cls._pw = None
