import unittest2
import os

import top


class TestConfig(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = os.path.join('top', 'conf', 'top.conf')

    def setUp(self):
        self._c = top.Config()

    def test_init(self):
        """Initialise a Config object.
        """
        msg = 'Object is not a top.Config'
        self.assertIsInstance(self._c, top.Config, msg)

    def test_parse_config_no_file(self):
        """Read config with no file provided.
        """
        self.assertRaises(SystemExit, self._c.parse_config)

    def test_read_config(self):
        """Read valid config.
        """
        old_config = self._c.config_file
        config = os.path.join('top', 'conf', 'top.conf')
        received = self._c.set_config_file(config)
        msg = 'Config should read without error and return None'
        self.assertIsNone(received, msg)

    def tearDown(self):
        self._c = None

    @classmethod
    def tearDownClass(cls):
        cls._file = None
        del cls._file
