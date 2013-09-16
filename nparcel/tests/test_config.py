import unittest2

import nparcel


class TestConfig(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._r = nparcel.Config()

    def test_init(self):
        """Initialise a Config object.
        """
        msg = 'Object is not a nparcel.Config'
        self.assertIsInstance(self._r, nparcel.Config, msg)

    def test_parse_config_no_file(self):
        """Read config with no file provided.
        """
        old_config = self._r.config_file
        self._r.set_config_file(None)

        self.assertRaises(SystemExit, self._r.parse_config)

        # Cleanup.
        self._r.set_config_file(old_config)

    def test_read_config(self):
        """Read valid config.
        """
        old_config = self._r.config_file
        received = self._r.set_config_file('nparcel/conf/nparceld.conf')
        msg = 'Config should read without error and return None'
        self.assertIsNone(received, msg)

        # Cleanup.
        self._r.set_config_file(old_config)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        del cls._r
