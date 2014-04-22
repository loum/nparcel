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

        received = self._c.comms_dir
        expected = '/data/nparcel/comms'
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

    def tearDown(self):
        del self._c
