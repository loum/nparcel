import unittest2

import nparcel


class TestSmser(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._sms = nparcel.Smser()

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
        """"Send SMS.
        """
        sms_msg = """Your consignment has been placed at Skylark News, 59 Skylark Street, INALA 4077. A Consignment Ref 4156736304. Please bring your photo ID with you. Enquiries 13 32 78"""
        self._sms.set_recipients(['0431602145'])

        received = self._sms.send(sms_msg, dry=True)
        msg = 'SMS send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._sms.set_recipients(None)

    @classmethod
    def tearDownClass(cls):
        cls._sms = None
