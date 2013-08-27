import unittest2

import nparcel


class TestEmailer(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._e = nparcel.Emailer()

    def test_init(self):
        """Verify initialisation of an nparcel.Emailer object.
        """
        msg = 'Object is not an nparcel.Emailer'
        self.assertIsInstance(self._e, nparcel.Emailer, msg)

    def test_send_without_sender_specified(self):
        """Send message without sender specified.
        """
        self._e.set_recipients(['banana'])
        self._e.send(subject='test subject', msg='banana msg', dry=True)

        msg = 'Sender should not be None'
        self.assertIsNotNone(self._e.sender, msg)

        # Clean up.
        self._e.set_recipients(None)

    def test_send_without_recipients(self):
        """Send message without recipients specified.
        """
        kwargs = {'subject': 'no recipients subject',
                  'msg': 'no recipients msg'}
        self._e.send(**kwargs)

    def test_send_with_empty_recipients_list(self):
        """Send message with empty recipients list specified.
        """
        self._e.set_recipients([])
        kwargs = {'subject': 'empty recipients list subject',
                  'msg': 'empty recipients list msg'}
        self._e.send(**kwargs)

        # Clean up.
        self._e.set_recipients(None)

    def test_email_validator_empty(self):
        """Validate email address -- empty.
        """
        msg = 'Empty email should not validate'

        email = ''
        received = self._e.validate(email)
        self.assertFalse(received, msg)

        email = 'banana'
        received = self._e.validate(email)
        self.assertFalse(received, msg)

    def test_email_validator(self):
        """Validate valid email.
        """
        msg = 'Email should validate'

        email = 'loumar@tollgroup.com'
        received = self._e.validate(email)
        self.assertTrue(email)

    def test_send(self):
        """Send an email.
        """
        self._e.set_recipients(['loumar@bananagroup.com'])
        received = self._e.send(subject='Test subject',
                                msg='Test',
                                dry=True)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

        # Clean up.
        self._e.set_recipients(None)

    @classmethod
    def tearDownClass(cls):
        cls._e = None
