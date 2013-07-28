__all__ = [
    "Cache",
]
import os

from  nparcel.utils.log import log


class Cache(object):
    """Nparcel Cache.

    The cache maintains a list of items that have been included in a
    previous extract.
    """

    def __init__(self, cache_file=None):
        """Cache object initialiser.

        If *cache_file* exists, it will make a backup copy to
        *cache_file*.prev in the same directory before attempting to open.

        **Args:**
            cache_file: name of the file that holds current cache data.

        """
        self._fh = None
        if cache_file is not None:
            if os.path.exists(cache_file):
                log.info('Found cache file "%s": ' % cache_file)
                self._fh = open(cache_file, 'wb')
