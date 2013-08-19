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
        self._e.set_recipients('banana')
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
        self.assertRaises(TypeError,
                          self._e.send,
                          **kwargs)

    @classmethod
    def tearDownClass(cls):
        cls._e = None
