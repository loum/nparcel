import unittest2

import nparcel


class TestConfig(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = 'nparcel/conf/nparceld.conf'

    def setUp(self):
        self._r = nparcel.Config()

    def test_init(self):
        """Initialise a Config object.
        """
        msg = 'Object is not a nparcel.Config'
        self.assertIsInstance(self._r, nparcel.Config, msg)

    def test_parse_config_no_file(self):
        """Read config with no file provided.
        """
        self.assertRaises(SystemExit, self._r.parse_config)

    def test_read_config(self):
        """Read valid config.
        """
        old_config = self._r.config_file
        received = self._r.set_config_file('nparcel/conf/nparceld.conf')
        msg = 'Config should read without error and return None'
        self.assertIsNone(received, msg)

    def tearDown(self):
        self._c = None

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        del cls._file
