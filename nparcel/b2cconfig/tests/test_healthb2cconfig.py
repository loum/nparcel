import unittest2
import os

import nparcel


class TestHealthB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = nparcel.HealthB2CConfig()

    def test_init(self):
        """Initialise a HealthB2CConfig object.
        """
        msg = 'Object is not a nparcel.HealthB2CConfig'
        self.assertIsInstance(self._c, nparcel.HealthB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('nparcel', 'conf', 'nparceld.conf')

        self._c.set_config_file(config_file)
        self._c.parse_config()

        received = self._c.support_emails
        expected = ['loumar@tollgroup.com']
        msg = 'email.support config error'
        self.assertListEqual(received, expected, msg)

        received = self._c.health_processes
        expected = ['npcommsd',
                    'npexporterd',
                    'npfilterd',
                    'nploaderd',
                    'npmapperd',
                    'npondeliveryd',
                    'npreminderd',
                    'nppoderd']
        msg = 'health.processes not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def tearDown(self):
        del self._c
