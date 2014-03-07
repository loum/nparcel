import unittest2
import os
import socket

import nparcel


class TestRestEmailer(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._re = nparcel.RestEmailer()

        # Uncomment these and set accordingly if you want to really send a
        # message.  BE CAREFUL!
        #proxy = 'loumar:P0o9i8U7@auproxy-farm.toll.com.au:8080'
        #cls._re._rest.set_proxy(proxy)
        #cls._re._rest.set_proxy_scheme('https')

        email_api = ('%s://%s' %
        ('https',
         'apps.cinder.co/tollgroup/wsemail/emailservice.svc/sendemail'))
        cls._re._rest.set_api(email_api)
        cls._re._rest.set_api_username('user')
        cls._re._rest.set_api_password('<pw>')

        cls._template_base = os.path.join('nparcel', 'templates')
        cls._re.set_template_base(cls._template_base)

        cls._hostname = socket.gethostname()

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
        f = open(os.path.join('nparcel',
                              'tests',
                              'files',
                              'encoded_params.out'))
        expected = f.read().rstrip()
        f.close()
        msg = 'Encoded message not as expected'
        self.assertEqual(received, expected, msg)

    def test_send_simple(self):
        """Send an email message to the REST-based interface.
        """
        dry = True

        subject = 'Test Message from Toll'
        sender = 'loumar@tollgroup.com'
        recipient = 'loumar@tollgroup.com'
        msg = 'TEST MESSAGE'

        received = self._re.send_simple(subject=subject,
                                        sender=sender,
                                        recipient=recipient,
                                        msg=msg,
                                        dry=dry)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

    def test_create_comms(self):
        """Send an email message to the REST-based interface.
        """
        subject = 'Test Message from Toll'
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr'}
        received = self._re.create_comms(subject=subject,
                                         data=d,
                                         prod=self._hostname)

        msg = 'Create comms should return a valid string'
        self.assertTrue(received, msg)

    def test_send(self):
        """Send an email message to the REST-based interface.
        """
        dry = True

        self._re.set_recipients(['loumar@tollgroup.com'])
        subject = 'Test Message from Toll'
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr'}
        encoded_msg = self._re.create_comms(subject=subject,
                                            data=d,
                                            prod=self._hostname)

        msg = 'Encoded e-mail message should not be None'
        self.assertIsNotNone(encoded_msg, msg)

        received = self._re.send(data=encoded_msg, dry=dry)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._re.set_recipients(None)
        self._re._rest.set_proxy_scheme('http')

    def test_send_non_prod_instance(self):
        """Send an email message to the REST-based interface -- non-PROD.
        """
        dry = True

        self._re.set_recipients(['loumar@tollgroup.com'])
        subject = 'Test Message from Toll'
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr'}
        encoded_msg = self._re.create_comms(subject=subject, data=d)

        msg = 'Encoded e-mail message should not be None'
        self.assertIsNotNone(encoded_msg, msg)

        received = self._re.send(data=encoded_msg, dry=dry)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._re.set_recipients(None)
        self._re._rest.set_proxy_scheme('http')

    def test_get_subject_line(self):
        """Build the subject line from a template -- base scenario.
        """
        d = {'connote_nbr': 'subject_connote'}
        received = self._re.get_subject_line(d, base_dir='nparcel')
        expected = 'Toll Consumer Delivery tracking # subject_connote'
        msg = 'Base body subject line not as expected'
        self.assertEqual(received, expected, msg)

    def test_check_subject(self):
        """Check subject context based on PROD and non-PROD instance.
        """
        subject = 'Subject'

        received = self._re.check_subject(subject, prod='banana')
        expected = 'TEST PLEASE IGNORE -- Subject'
        msg = 'Non-PROD subject error'
        self.assertEqual(received, expected, msg)

        received = self._re.check_subject(subject, prod=self._hostname)
        expected = subject
        msg = 'PROD subject error'
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        del cls._re
        del cls._hostname
