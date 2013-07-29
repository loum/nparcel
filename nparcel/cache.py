__all__ = [
    "Cache",
]
import pickle

from  nparcel.utils.log import log


class Cache(object):
    """Nparcel Cache.

    The cache maintains a list of items that have been included in a
    previous extract.
    """

    def __init__(self, cache_file=None):
        """Cache object initialiser.

        For writes, if *cache_file* exists then a backup copy to
        *cache_file*.prev in the same directory is made.

        **Args:**
            cache_file: name of the file that holds current cache data.

        """
        self._cache_file = cache_file
        self._cache = None

    def __call__(self):
        """Cache object callable that attempts to open the file cache
        and load the :mod:`pickle` object data.

        """
        log.info('Attempting cache load from "%s" ...' % self._cache_file)

        if self._cache_file is not None:
            try:
                fh = open(self._cache_file, 'rb')
                self._cache = pickle.load(self._fh)
            except IOError, e:
                log.error('Could not read file "%s"' % self._cache_file)
                pass

        return self._cache

    def set_cache_file(self, cache_file):
        self._cache_file = cache_file
