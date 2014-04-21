import unittest2
import os

import nparcel


class TestPodB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = nparcel.PodB2CConfig()

    def test_init(self):
        """Initialise a PodB2CConfig object.
        """
        msg = 'Object is not a nparcel.PodB2CConfig'
        self.assertIsInstance(self._c, nparcel.PodB2CConfig, msg)

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

        received = self._c.pod_translator_loop
        expected = 600
        msg = 'pod_translator_loop config error'
        self.assertEqual(received, expected, msg)

        received = self._c.pod_dirs
        expected = [os.path.join(os.sep,
                                 'var',
                                 'ftp',
                                 'pub',
                                 'nparcel',
                                 'parcelpoint',
                                 'in')]
        msg = 'dirs.pod_in config error'
        self.assertListEqual(received, expected, msg)

        received = self._c.out_dir
        expected = os.path.join(os.sep,
                                'var',
                                'ftp',
                                'pub',
                                'nparcel',
                                'fast',
                                'out')
        msg = 'pods.out_dir config error'
        self.assertEqual(received, expected, msg)

        received = self._c.file_formats
        expected = ['.*_REF_\\d{14}\\.txt$']
        msg = 'pods.file_formats config error'
        self.assertListEqual(received, expected, msg)

    def tearDown(self):
        del self._c
