import unittest2

import top


class TestEmailerBase(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._e = top.EmailerBase()

    def test_init(self):
        """Verify initialisation of an top.EmailerBase object.
        """
        msg = 'Object is not an top.EmailerBase'
        self.assertIsInstance(self._e, top.EmailerBase, msg)

    def test_validate(self):
        """Validate email addresses.
        """
        # Valid address.
        email = 'lou.markovski@tollgroup.com'
        received = self._e.validate(email)
        msg = 'Valid email should return True'
        self.assertTrue(received)

        # Invalid -- too many @'s.
        email = '@@@tollgroup.com'
        received = self._e.validate(email)
        msg = 'Invalid email (too many @s) should return False'
        self.assertFalse(received)

        # Valid -- hyphen in local-part.
        email = 'local-part@tollgroup.com'
        received = self._e.validate(email)
        msg = 'Valid email (hyphen in local-part) should return True'
        self.assertTrue(received)

        # Valid -- hyphen in domain-part.
        email = 'localpart@domain-part.com'
        received = self._e.validate(email)
        msg = 'Valid email (hyphen in domain-part) should return True'
        self.assertTrue(received)

        # Valid -- multiple dots in domain part
        email = 'localpart@domain-part.com.au'
        received = self._e.validate(email)
        msg = 'Valid email (multiple dots domain part) should return True'
        self.assertTrue(received)

        # Valid -- multiple dots in domain part
        email = 'AUTO_417A82AA-1D95-425B-AA67-D590AD955308@autoidn.'
        received = self._e.validate(email)
        msg = 'Valid email (multiple dots domain part) should return True'
        self.assertFalse(received)

        # Valid -- dot and hyphen.
        email = 'wesley.marley-wallace@tollgroup.com'
        received = self._e.validate(email)
        msg = 'Valid email (dot and hyphen in name) should return True'
        self.assertTrue(received)

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

    @classmethod
    def tearDownClass(cls):
        cls._e = None
        del cls._e
