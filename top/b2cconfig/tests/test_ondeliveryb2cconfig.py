import unittest2
import os

import top


class TestOnDeliveryB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = top.OnDeliveryB2CConfig()

    def test_init(self):
        """Initialise a OnDeliveryB2CConfig object.
        """
        msg = 'Object is not a top.OnDeliveryB2CConfig'
        self.assertIsInstance(self._c, top.OnDeliveryB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('top', 'conf', 'top.conf')

        self._c.set_config_file(config_file)
        self._c.parse_config()

        received = self._c.business_units
        expected = {'priority': 1, 'fast': 2, 'ipec': 3}
        msg = 'OnDelivery business_units error'
        self.assertDictEqual(received, expected, msg)

        received = self._c.comms_delivery_partners
        expected = {'priority': ['Nparcel'],
                    'fast': ['Nparcel'],
                    'ipec': ['Nparcel']}
        msg = 'OnDelivery comms_delivery_partners error'
        self.assertDictEqual(received, expected, msg)

        received = self._c.comms_dir
        expected = '/data/top/comms'
        msg = 'OnDelivery comms_dir error'
        self.assertEqual(received, expected, msg)

        # For the default configuration file the [db] section is blank
        received = self._c.db_kwargs()
        msg = 'OnDelivery db_kwargs error'
        self.assertIsNone(received, msg)

        received = self._c.ondelivery_loop
        expected = 30
        msg = 'OnDelivery loop error'
        self.assertEqual(received, expected, msg)

        received = self._c.inbound_tcd
        expected = ['/var/ftp/pub/nparcel/tcd/in']
        msg = 'OnDelivery inbound_tcd error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._c.tcd_filename_format
        expected = 'TCD_Deliveries_\d{14}\.DAT'
        msg = 'OnDelivery tcd_filename_format error'
        self.assertEqual(received, expected, msg)

        received = self._c.pe_comms_ids
        expected = (1, 2, 3)
        msg = 'OnDelivery pe_comms_ids error'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.sc4_comms_ids
        expected = ()
        msg = 'OnDelivery sc4_comms_ids error'
        self.assertTupleEqual(received, expected, msg)

        received = self._c.uncollected_day_range
        expected = 14.0
        msg = 'OnDelivery uncollected_day_range error'
        self.assertEqual(received, expected, msg)

        received = self._c.file_cache_size
        expected = 5
        msg = 'OnDelivery file_cache_size error'
        self.assertEqual(received, expected, msg)

        received = self._c.delivered_header
        expected = 'latest_scan_event_action'
        msg = 'OnDelivery delivered_header error'
        self.assertEqual(received, expected, msg)

        received = self._c.delivered_event_key
        expected = 'delivered'
        msg = 'OnDelivery delivered_event_key error'
        self.assertEqual(received, expected, msg)

        received = self._c.scan_desc_header.lower()
        expected = 'latest_scanner_description'
        msg = 'OnDelivery scan_desc_header error'
        self.assertEqual(received, expected, msg)

        received = self._c.scan_desc_keys
        expected = ['IDS - TOLL FAST GRAYS ONLINE']
        msg = 'OnDelivery scan_desc_keys error'
        self.assertListEqual(received, expected, msg)

        received = self._c.sc4_delay_ids
        expected = ()
        msg = 'OnDelivery sc4_delay_ids error'
        self.assertTupleEqual(received, expected, msg)

    def tearDown(self):
        del self._c
