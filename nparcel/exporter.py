__all__ = [
    "Exporter",
]
import nparcel
from nparcel.utils.log import log


class Exporter(object):
    """Nparcel Exporter.
    """

    def __init__(self, db=None, cache_file=None):
        """Exporter object initialiser.
        """
        log.debug('Creating an Exporter object')
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self._cached_items = nparcel.Cache(cache_file)

        self._collected_items = []

    def get_collected_items(self, range=86400):
        """Query DB for recently collected items.

        """
        # First, source our cache.
        cached_items = self._cached_items()

        sql = self.db.jobitem.collected_sql(range=range)
        self.db(sql)

        items = []
        for row in self.db.rows():
            is_cached = False
            item_id = row[0]

            if cached_items and cached_items.get(item_id) is None:
                is_cached = True

            if not is_cached:
                self._collected_items.append(item_id)
