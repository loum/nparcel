import unittest2
import os

import top


class TestHealthB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = top.HealthB2CConfig()

    def test_init(self):
        """Initialise a HealthB2CConfig object.
        """
        msg = 'Object is not a top.HealthB2CConfig'
        self.assertIsInstance(self._c, top.HealthB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('top', 'conf', 'top.conf')

        self._c.set_config_file(config_file)
        self._c.parse_config()

        received = self._c.health_processes
        expected = ['topcommsd',
                    'topexporterd',
                    'topfilterd',
                    'toploaderd',
                    'topmapperd',
                    'topondeliveryd',
                    'topreminderd',
                    'toppoderd']
        msg = 'health.processes not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def tearDown(self):
        del self._c
