import unittest2
import os

import nparcel


class TestFilterB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = nparcel.FilterB2CConfig()

    def test_init(self):
        """Initialise a FilterB2CConfig object.
        """
        msg = 'Object is not a nparcel.FilterB2CConfig'
        self.assertIsInstance(self._c, nparcel.FilterB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('nparcel', 'conf', 'top.conf')

        self._c.set_config_file(config_file)
        self._c.parse_config()

        received = self._c.t1250_file_format
        expected = 'T1250_TOL.*\.txt$'
        msg = 'OnDeliveryB2CConfig.t1250_file_format error'
        self.assertEqual(received, expected, msg)

        received = self._c.staging_base
        expected = '/var/ftp/pub/nparcel'
        msg = 'OnDeliveryB2CConfig.staging_base error'
        self.assertEqual(received, expected, msg)

        received = self._c.aggregator_dirs
        expected = ['/data/nparcel/aggregate']
        msg = 'OnDeliveryB2CConfig.aggregator_dirs error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._c.filters
        expected = {'parcelpoint': ['P', 'R'],
                    'woolworths': ['U']}
        msg = 'OnDeliveryB2CConfig.filter_customer error'
        self.assertEqual(received, expected, msg)

        received = self._c.support_emails
        expected = ['loumar@tollgroup.com']
        msg = 'OnDeliveryB2CConfig.supoprt_emails error'
        self.assertListEqual(received, expected, msg)

        received = self._c.filter_loop
        expected = 30
        msg = 'Filter loop error'
        self.assertEqual(received, expected, msg)

    def tearDown(self):
        del self._c
