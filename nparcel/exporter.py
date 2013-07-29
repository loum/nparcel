__all__ = [
    "Exporter",
]
import re
import os
import datetime

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
                 staging_dir=None):
        """Exporter object initialiser.
        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self._cache = nparcel.Cache(cache_file)
        self._staging_dir = staging_dir

        self._collected_items = []

    def set_staging_dir(self, value):
        self._staging_dir = value

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
        file_name = None

        header = '|'.join(FIELDS)

        if self._staging_dir is None:
            print(header)
            for item in self._collected_items:
                print('%s' % '|'.join(map(str, item)))
        else:
            fh = self.outfile(self._staging_dir)
            file_name = fh.name
            fh.write('%s\n' % header)
            for item in self._collected_items:
                fh.write('%s\n' % '|'.join(map(str, item)))
            fh.close()

            # Finally, rename the output file so that it's ready for
            # delivery.
            target_file = file_name.replace('.txt.tmp', '.txt')
            log.info('Renaming out file to "%s"' % target_file)
            os.rename(file_name, target_file)

        return file_name

    def outfile(self, dir):
        """Creates the Exporter output file based on current timestamp
        and verifies creation at the staging directory *dir*.

        During output file access, prepends ``.tmp`` to the file.

        **Args:**
            dir: name of the staging directory

        **Returns:**
            open file handle to the exporter report file (or None if file
            access fails)

        """
        status = True
        fh = None

        # Attempt to create the staging directory if it does not exist.
        if not os.path.exists(dir):
            try:
                log.info('Creating staging directory "%s"' % dir)
                os.makedirs(dir)
            except OSError, err:
                status = False
                log.error('Unable to create staging directory "%s": %s"' %
                          (dir, err))

        if status:
            # Create the output file.
            time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            file = "%s_%s_%s_%s.txt.tmp" % ('VIC', 'VANA', 'REP', time)
            file_path = os.path.join(dir, file)
            try:
                log.info('Opening file "%s"' % file_path)
                fh = open(file_path, 'wb')
            except IOError, err:
                status= False
                log.error('Could not open out file "%s": %s' )

        return fh
