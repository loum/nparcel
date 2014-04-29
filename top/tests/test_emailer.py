import unittest2
import os
import socket

import top


class TestEmailer(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._e = top.Emailer()
        cls._e.set_recipients(['loumar@tollgroup.com'])
        cls._e.set_template_base(os.path.join('top', 'templates'))

        cls._hostname = socket.gethostname()

    def test_init(self):
        """Verify initialisation of an top.Emailer object.
        """
        msg = 'Object is not an top.Emailer'
        self.assertIsInstance(self._e, top.Emailer, msg)

    def test_send(self):
        """Send an email.
        """
        # To check that email alerts are sent set dry to False.
        dry = True

        received = self._e.send(subject='Test subject', msg='Test', dry=dry)
        msg = 'Email send should return True'
        self.assertTrue(received, msg)

    def test_send_without_recipients(self):
        """Send message without recipients specified.
        """
        dry = True

        old_recipients = self._e.recipients
        self._e.set_recipients([])
        kwargs = {'subject': 'no recipients subject',
                  'msg': 'no recipients msg'}

        received = self._e.send(**kwargs)
        msg = 'E-mail send with no recipients should return False'
        self.assertFalse(received, msg)

        # Clean up.
        self._e.set_recipients(old_recipients)

    def test_send_test_template(self):
        """Test send -- test template.
        """
        # We don't really test anything here.  But, to check that
        # email alerts are sent set dry to False.
        dry = True

        data = {}
        mime = self._e.create_comms(data, template='test')
        self._e.send(mime_message=mime, dry=dry)

    def test_send_with_attachment(self):
        """Test send -- with attachment.
        """
        # We don't really test anything here.  But, to check that
        # email alerts are sent set dry to False.
        dry = True

        data = {}
        file = [os.path.join('top', 'tests', 'files', 'test.xlsx')]
        mime = self._e.create_comms(data, template='test', files=file)
        received = self._e.send(mime_message=mime, dry=dry)
        msg = 'E-mail send with attachment should return True'
        self.assertTrue(received, msg)

    def test_send_with_attachment_prod(self):
        """Test send -- with attachment (prod).
        """
        # We don't really test anything here.  But, to check that
        # email alerts are sent set dry to False.
        dry = True

        data = {}
        file = [os.path.join('top', 'tests', 'files', 'test.xlsx')]
        mime = self._e.create_comms(data,
                                    template='test',
                                    files=file,
                                    prod=self._hostname)
        received = self._e.send(mime_message=mime, dry=dry)
        msg = 'E-mail send with attachment should return True (prod)'
        self.assertTrue(received, msg)

    def test_send_override_subject(self):
        """Test send override subject.
        """
        # We don't really test anything here.  But, to check that
        # email alerts are sent set dry to False.
        dry = True

        subject = 'Override subject'
        data = {}
        mime = self._e.create_comms(data=data,
                                    subject=subject,
                                    template='test')
        received = self._e.send(mime_message=mime, dry=dry)
        msg = 'E-mail send override subject should return True'
        self.assertTrue(received, msg)

    def test_check_subject(self):
        """Check subject context based on PROD and non-PROD instance.
        """
        subject = 'Subject'

        received = self._e.check_subject(subject, prod='banana')
        expected = 'TEST PLEASE IGNORE -- Subject'
        msg = 'Non-PROD subject error'
        self.assertEqual(received, expected, msg)

        received = self._e.check_subject(subject, prod=self._hostname)
        expected = subject
        msg = 'PROD subject error'
        self.assertEqual(received, expected, msg)

    def test_get_subject_line(self):
        """Build the subject line from a template -- base scenario.
        """
        d = {'connote_nbr': 'subject_connote'}
        received = self._e.get_subject_line(d)
        expected = 'Toll Consumer Delivery tracking # subject_connote'
        msg = 'Base body subject line not as expected'
        self.assertEqual(received, expected, msg)

    def test_get_subject_line_errored(self):
        """Build the subject line from a template -- errored scenario.
        """
        d = {'connote_nbr': 'subject_connote'}
        err_string = 'FAILED NOTIFICATION -- '
        received = self._e.get_subject_line(d, err=True)
        expected = ('%sToll Consumer Delivery tracking # subject_connote' %
                    err_string)
        msg = 'Errored subject line not as expected'
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        del cls._e
        del cls._hostname
