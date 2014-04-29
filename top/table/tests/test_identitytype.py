import unittest2

import nparcel


class TestIdentityType(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._identity_type = nparcel.IdentityType()

    def test_init(self):
        """Test initialisation of an IdentityType object.
        """
        msg = 'Object is not an nparcel.IdentityType'
        self.assertIsInstance(self._identity_type,
                              nparcel.IdentityType,
                              msg)

    @classmethod
    def tearDownClass(cls):
        cls._ientity_type = None
