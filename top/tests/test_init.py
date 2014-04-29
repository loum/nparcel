import unittest2
import tempfile
import os

import top
from top.utils.files import remove_files


class TestInit(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._i = top.Init(os.path.join('top',
                                       'conf',
                                       'init.conf'))
        cls._i.parse_config()

    def test_init(self):
        """Initialise an Init object.
        """
        msg = 'Object is not an top.Init'
        self.assertIsInstance(self._i, top.Init, msg)

    def test_parse_config(self):
        """Read config items from the initialisation configuration file.
        """
        received = self._i.unconditional_files
        expected = []
        msg = 'Unconditional files error'
        self.assertListEqual(received, expected, msg)

        received = self._i.unconditional_dirs
        expected = ['top/conf', 'top/utils/conf']
        msg = 'Unconditional directory error'
        self.assertListEqual(received, expected, msg)

        received = self._i.conditional_files
        expected = []
        msg = 'Conditional files error'
        self.assertListEqual(received, expected, msg)

        received = self._i.conditional_dirs
        expected = ['top/templates']
        msg = 'Conditional directory error'
        self.assertListEqual(received, expected, msg)

    def test_copy_file(self):
        """Copy file -- unconditional.
        """
        dir = tempfile.mkdtemp()
        source_file = tempfile.NamedTemporaryFile()
        source_file_name = source_file.name

        old_base_dir = self._i.base_dir
        self._i.set_base_dir(dir)

        received = self._i.copy_file(source_file_name,
                                     dir,
                                     conditional=False)
        msg = 'Unconditional file copy should return True'
        self.assertTrue(received, msg)

        # Now copy the same unconditionally.
        received = self._i.copy_file(source_file_name,
                                     dir,
                                     conditional=False)
        msg = 'Unconditional secondary file copy should return True'
        self.assertTrue(received, msg)

        # ... and copy the same conditionally.
        received = self._i.copy_file(source_file_name,
                                     dir,
                                     conditional=True)
        msg = 'Conditional secondary file copy should return False'
        self.assertFalse(received, msg)

        # Clean up.
        remove_files([os.path.join(dir, x) for x in os.listdir(dir)])
        self._i.set_base_dir(old_base_dir)
        os.removedirs(dir)

    @classmethod
    def tearDownClass(cls):
        cls._i = None
        del cls._i
