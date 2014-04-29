import unittest2
import os
import socket

import top


class TestRestEmailer(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._re = top.RestEmailer()

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

        cls._template_base = os.path.join('top', 'templates')
        cls._re.set_template_base(cls._template_base)

        cls._hostname = socket.gethostname()

    def test_init(self):
        """Verify initialisation of an top.RestEmailer object.
        """
        msg = 'Object is not an top.RestEmailer'
        self.assertIsInstance(self._re, top.RestEmailer, msg)

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
        f = open(os.path.join('top',
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
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr'}
        received = self._re.create_comms(data=d,
                                         prod=self._hostname)

        msg = 'Create comms should return a valid string'
        self.assertTrue(received, msg)

    def test_send(self):
        """Send an email message to the REST-based interface.
        """
        dry = True

        self._re.set_recipients(['loumar@tollgroup.com'])
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr'}
        encoded_msg = self._re.create_comms(data=d,
                                            prod=self._hostname)

        msg = 'Encoded e-mail message should not be None'
        self.assertIsNotNone(encoded_msg, msg)

        received = self._re.send(data=encoded_msg, dry=dry)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._re.set_recipients(None)

    def test_send_error(self):
        """Send an email message to the REST-based interface -- error.
        """
        dry = True

        self._re.set_recipients(['loumar@tollgroup.com'])
        d = {'bad_email_addr': 'loumar@tollgroup.com',
             'error_comms': 'Email',
             'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr',
             'phone_nbr': '0431602145',
             'email_addr': 'loumar@tollgroup.com',
             'bu_id': 1}
        encoded_msg = self._re.create_comms(data=d,
                                            err=True,
                                            prod=self._hostname)

        msg = 'Encoded e-mail error message should not be None'
        self.assertIsNotNone(encoded_msg, msg)

        received = self._re.send(data=encoded_msg, dry=dry)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._re.set_recipients(None)

    def test_send_non_prod_instance(self):
        """Send an email message to the REST-based interface -- non-PROD.
        """
        dry = True

        self._re.set_recipients(['loumar@tollgroup.com'])
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr'}
        encoded_msg = self._re.create_comms(data=d)

        msg = 'Encoded e-mail message should not be None'
        self.assertIsNotNone(encoded_msg, msg)

        received = self._re.send(data=encoded_msg, dry=dry)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._re.set_recipients(None)

    def test_send_non_prod_instance_error(self):
        """Send an email message to the REST-based interface --
        non-PROD / error.
        """
        dry = True

        self._re.set_recipients(['loumar@tollgroup.com'])
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr',
             'error_comms': 'Email',
             'bu_id': 1,
             'phone_nbr': '0431602145',
             'bad_email_addr': 'loumar@tollgroup.com'}
        encoded_msg = self._re.create_comms(data=d, err=True)

        msg = 'Encoded e-mail message should not be None'
        self.assertIsNotNone(encoded_msg, msg)

        received = self._re.send(data=encoded_msg, dry=dry)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._re.set_recipients(None)

    @classmethod
    def tearDownClass(cls):
        del cls._re
        del cls._template_base
        del cls._hostname
