import unittest2
import os

import nparcel


class TestExporterB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = nparcel.ExporterB2CConfig()

    def test_init(self):
        """Initialise a ExporterB2CConfig object.
        """
        msg = 'Object is not a nparcel.ExporterB2CConfig'
        self.assertIsInstance(self._c, nparcel.ExporterB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('nparcel', 'conf', 'nparceld.conf')

        self._c.set_config_file(config_file)
        self._c.parse_config()

        received = self._c.signature_dir
        expected = os.path.join(os.sep,
                                'data',
                                'www',
                                'nparcel',
                                'data',
                                'signature')
        msg = 'dir.signature error'
        self.assertEqual(received, expected, msg)

        received = self._c.file_bu
        expected = {'tolf': 2,
                    'tolf_act': 2,
                    'tolf_nsw': 2,
                    'tolf_qld': 2,
                    'tolf_sa': 2,
                    'tolf_vic': 2,
                    'tolf_wa': 2,
                    'toli': 3,
                    'tolp': 1}
        msg = 'dir.file_bu error'
        self.assertDictEqual(received, expected, msg)

        received = self._c.exporter_dirs
        expected = [os.path.join(os.sep, 'data', 'nparcel', 'exporter')]
        msg = 'dir.exporter_in error'
        self.assertListEqual(received, expected, msg)

        received = self._c.connote_header
        expected = 'REF1'
        msg = 'exporter.connote_header error'
        self.assertEqual(received, expected, msg)

        received = self._c.exporter_file_formats
        expected = ['.*_RE[PIF]_\d{14}\.txt$']
        msg = 'exporter.file_formats error'
        self.assertListEqual(received, expected, msg)

        received = self._c.item_nbr_header
        expected = 'ITEM_NBR'
        msg = 'exporter.item_nbr header error'
        self.assertEqual(received, expected, msg)

        received = self._c.business_units
        expected = {'priority': 1, 'fast': 2, 'ipec': 3}
        msg = 'business_units config section error'
        self.assertDictEqual(received, expected, msg)

        received = self._c.cond
        expected = {'tolp': '000100000000010110',
                    'tolf': '000101100000010110',
                    'toli': '100010000000010110'}
        msg = 'conditions config section error'
        self.assertDictEqual(received, expected, msg)

    def tearDown(self):
        del self._c
