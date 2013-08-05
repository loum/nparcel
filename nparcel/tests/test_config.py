import unittest2

import nparcel


class TestConfig(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/conf/nparceld.conf'
        cls._c = nparcel.Config()

    def test_init(self):
        """Initialise a Config object.
        """
        msg = 'Object is not a nparcel.Config'
        self.assertIsInstance(self._c, nparcel.Config, msg)

    def test_set_missing_config_file(self):
        """Set missing config file.
        """
        self.assertRaises(SystemExit, self._c.set_file, 'dodgy')

    def test_set_valid_config_file(self):
        """Set a valid config file.
        """
        msg = 'Valid config file assignment should return None'
        self.assertIsNone(self._c.set_file(file=self._file), msg)

        # Cleanup.
        self._c._file = None

    def test_parse_config_no_file(self):
        """Parse items from the config -- no file.
        """
        self.assertRaises(SystemExit, self._c.parse_config)

    def test_parse_config(self):
        """Parse items from the config.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        # Check against expected config items.
        msg = 'Directories to check not as expected'
        received = self._c('in_dirs')
        expected = ['/var/ftp/pub/nparcel/priority/in']
        self.assertListEqual(received, expected, msg)

        msg = 'Archive directory not as expected'
        received = self._c('archive_dir')
        expected = '/data/nparcel/archive'
        self.assertEqual(received, expected, msg)

        msg = 'Signature directory not as expected'
        received = self._c('signature_dir')
        expected = '/data/www/nparcel/data/signature'
        self.assertEqual(received, expected, msg)

        msg = 'Staging base directory not as expected'
        received = self._c('staging_base')
        expected = '/var/ftp/pub/nparcel'
        self.assertEqual(received, expected, msg)

        msg = 'Loader loop not as expected'
        received = self._c('loader_loop')
        expected = 30
        self.assertEqual(received, expected, msg)

        msg = 'Exporter loop not as expected'
        received = self._c('exporter_loop')
        expected = 300
        self.assertEqual(received, expected, msg)

        msg = 'Business units not as expected'
        received = self._c('business_units')
        expected = {'priority': '1', 'fast': '2', 'ipec': '3'}
        self.assertDictEqual(received, expected, msg)

        # Cleanup.
        self._c._file = None

    def test_db_kwargs_no_items(self):
        """Produce a DB connection string -- no items.
        """
        self._c.set_file(file=self._file)
        self._c.parse_config()

        msg = 'DB connection string should be None'
        self.assertIsNone(self._c.db_kwargs(), msg)

        # Cleanup.
        self._c._file = None

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        cls._c = None
