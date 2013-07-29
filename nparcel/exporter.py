__all__ = [
    "Exporter",
]
import re

import nparcel
from nparcel.utils.log import log

FIELDS = ['REF1',
          'JOB_KEY',
          'PICKUP_TIME',
          'PICKUP_POD',
          'IDENTITY_TYPE',
          'IDENTITY_DATA']


class Exporter(object):
    """Nparcel Exporter.
    """

    def __init__(self,
                 db=None,
                 cache_file=None,
                 out_file=None):
        """Exporter object initialiser.
        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self._cache = nparcel.Cache(cache_file)
        self._out_file = out_file

        self._collected_items = []

    def get_collected_items(self, range=86400):
        """Query DB for recently collected items.

        """
        # First, source our cache.
        cached_items = self._cache()

        sql = self.db.jobitem.collected_sql(range=range)
        self.db(sql)

        items = []
        for row in self.db.rows():
            cleansed_row = self._cleanse(row)

            is_cached = False
            item_id = cleansed_row[1]

            if cached_items and cached_items.get(item_id) is None:
                is_cached = True

            if not is_cached:
                self._collected_items.append(cleansed_row)

    def _cleanse(self, row):
        """Runs over the "jobitem" record and modifies to suit the
        requirements of the report.

        **Args:**
            row: tuple representing the columns from the "jobitem" table
            record.

        **Returns:**
            tuple representing the cleansed data suitable for Nparcel
            exporter output.

        """
        log.debug('cleansing row: "%s"' % str(row))
        row_list = list(row)

        # "pickup_ts" column should have microseconds removed.
        m = re.match('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d*', row_list[2])
        try:
            pickup_ts = m.group(1)
            log.debug('Cleansed pickup_ts produced "%s"' % pickup_ts)
            row_list[2] = pickup_ts
        except AttributeError, err:
            log.error('Error cleansing pickup_ts "%s": %s' % (row[2], err))

        return tuple(row_list)

    def report(self):
        """Cycle through the newly identified collected items and produce
        a report.

        """
        header = '|'.join(FIELDS)

        if self._out_file is None:
            print(header)
            for item in self._collected_items:
                print('%s' % '|'.join(map(str, item)))
