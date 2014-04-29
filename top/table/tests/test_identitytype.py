import unittest2

import top


class TestIdentityType(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._identity_type = top.IdentityType()

    def test_init(self):
        """Test initialisation of an IdentityType object.
        """
        msg = 'Object is not an top.IdentityType'
        self.assertIsInstance(self._identity_type,
                              top.IdentityType,
                              msg)

    @classmethod
    def tearDownClass(cls):
        cls._ientity_type = None
