import unittest2
import os

import nparcel


class TestOnDeliveryB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = nparcel.OnDeliveryB2CConfig()

    def test_init(self):
        """Initialise a OnDeliveryB2CConfig object.
        """
        msg = 'Object is not a nparcel.OnDeliveryB2CConfig'
        self.assertIsInstance(self._c, nparcel.OnDeliveryB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('nparcel', 'conf', 'nparceld.conf')

        self._c.set_config_file(config_file)
        self._c.parse_config()

        msg = 'On delivery loop not as expected'
        received = self._c.ondelivery_loop
        expected = 30
        self.assertEqual(received, expected, msg)

    def tearDown(self):
        del self._c
