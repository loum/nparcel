import unittest2
import os


import nparcel


class TestMapperB2CConfig(unittest2.TestCase):

    def setUp(self):
        self._c = nparcel.MapperB2CConfig()

    def test_init(self):
        """Initialise a MapperB2CConfig object.
        """
        msg = 'Object is not a nparcel.MapperB2CConfig'
        self.assertIsInstance(self._c, nparcel.MapperB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('nparcel', 'conf', 'top.conf')
        self._c.set_config_file(config_file)
        self._c.parse_config()

        received = self._c.mapper_loop
        expected = 30
        msg = 'timeout.mapper_loop error'
        self.assertEqual(received, expected, msg)

        received = self._c.pe_customer
        expected = 'gis'
        msg = 'primary_elect.customer error'
        self.assertEqual(received, expected, msg)

        received = self._c.mapper_in_dirs
        expected = ['/var/ftp/pub/nparcel/gis/in']
        msg = 'dir.mapper_in error'
        self.assertListEqual(received, expected, msg)

        received = self._c.pe_in_file_format
        expected = 'T1250_TOL[PIF]_\d{14}\.dat'
        msg = 'primary.elect_file_format error'
        self.assertEqual(received, expected, msg)

        received = self._c.archive_dir
        expected = '/data/nparcel/archive'
        msg = 'dirs.archive error'
        self.assertEqual(received, expected, msg)

        received = self._c.pe_in_file_archive_string
        expected = 'T1250_TOL[PIF]_(\\d{8})\\d{6}\\.dat'
        msg = 'dirs.pe_in_file_archive_string error'
        self.assertEqual(received, expected, msg)

    def tearDown(self):
        del self._c
