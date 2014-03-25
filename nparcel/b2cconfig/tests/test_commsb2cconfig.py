import unittest2
import os

import nparcel


class TestCommsB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = nparcel.CommsB2CConfig()

    def test_init(self):
        """Initialise a CommsB2CConfig object.
        """
        msg = 'Object is not a nparcel.CommsB2CConfig'
        self.assertIsInstance(self._c, nparcel.CommsB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('nparcel', 'conf', 'nparceld.conf')

        self._c.set_config_file(config_file)
        self._c.parse_config()

        received = self._c.prod
        expected = 'faswbaup02'
        msg = 'environment.prod not as expected'
        self.assertEqual(received, expected, msg)

        received = self._c.support_emails
        expected = ['loumar@tollgroup.com']
        msg = 'emails.support not as expected'
        self.assertListEqual(received, expected, msg)

        received = self._c.comms_dir
        expected = os.path.join(os.sep, 'data', 'nparcel', 'comms')
        msg = 'dir.comms not as expected'
        self.assertEqual(received, expected, msg)

        received = self._c.comms_loop
        expected = 30
        msg = 'timeout.comms_loop not as expected'
        self.assertEqual(received, expected, msg)

        received = self._c.comms_q_warning
        expected = 100
        msg = 'Comms message queue warning error'
        self.assertEqual(received, expected, msg)

        received = self._c.comms_q_error
        expected = 1000
        msg = 'Comms message queue error error'
        self.assertEqual(received, expected, msg)

        received = self._c.controlled_templates
        expected = ['body', 'rem', 'delay', 'pe']
        msg = 'comms.controlled_templates not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._c.uncontrolled_templates
        expected = ['ret']
        msg = 'comms.uncontrolled_templates not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._c.skip_days
        expected = ['Sunday']
        msg = 'comms.skip_days not as expected'
        self.assertListEqual(received, expected, msg)

        received = self._c.send_time_ranges
        expected = ['08:00-19:00']
        msg = 'comms.send_time_ranges not as expected'
        self.assertListEqual(received, expected, msg)

    def tearDown(self):
        del self._c
