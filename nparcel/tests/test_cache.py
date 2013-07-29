import unittest2
import tempfile

import nparcel


class TestCache(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._c = nparcel.Cache()

        # Create a random cache file.
        f = tempfile.NamedTemporaryFile()
        cls._cache_file = f.name

    def test_init(self):
        """Initialise a Cache object.
        """
        msg = "Object is not an nparcel.Cache()"
        self.assertIsInstance(self._c, nparcel.Cache, msg)

    def test_cache_file_open_missing_file(self):
        """Attempt to open a missing cache file.
        """
        self._c.set_cache_file(self._cache_file)
        msg = 'Data should be none for newly assigned file'
        self.assertIsNone(self._c(), msg)

    def test_cached_items_if_file_not_provided(self):
       """Check cached items if a cache file is not provided.
       """
       msg = "Cached data object should return None"
       self.assertIsNone(self._c(), msg)

    @classmethod
    def tearDownClass(cls):
        cls._c = None
        cls._cache_file = None
