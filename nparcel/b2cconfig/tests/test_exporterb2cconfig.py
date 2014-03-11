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
        expected = '/data/www/nparcel/data/signature'
        msg = 'dir.signature error'
        self.assertEqual(received, expected, msg)

        received = self._c.exporter_file_formats
        expected = ['.*_RE[PIF]_\d{14}\.txt$']
        msg = 'exporter.file_formats error'
        self.assertListEqual(received, expected, msg)

        received = self._c.connote_header
        expected = 'REF1'
        msg = 'exporter.connote_header error'
        self.assertEqual(received, expected, msg)

        received = self._c.item_nbr_header
        expected = 'ITEM_NBR'
        msg = 'exporter.item_nbr header error'
        self.assertEqual(received, expected, msg)

    def tearDown(self):
        del self._c
