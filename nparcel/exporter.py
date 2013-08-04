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
                 signature_dir=None,
                 staging_dir=None):
        """Exporter object initialiser.
        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self._signature_dir = signature_dir
        self._staging_dir = staging_dir
        self._create_dir(self._staging_dir)

        self._collected_items = []

    @property
    def signature_dir(self):
        return self._signature_dir

    def set_signature_dir(self, value):
        self._signature_dir = value

    @property
    def staging_dir(self):
        return self._staging_dir

    def set_staging_dir(self, value):
        self._staging_dir = value

        self._create_dir(dir=self._staging_dir)

    def get_collected_items(self, business_unit):
        """Query DB for recently collected items.

        """
        sql = self.db.jobitem.collected_sql(business_unit=business_unit)
        self.db(sql)

        items = []
        for row in self.db.rows():
            cleansed_row = self._cleanse(row)

            item_id = cleansed_row[1]

            self._collected_items.append(cleansed_row)
            id = row[1]
            if self.move_signature_file(id):
                self._update_status(id)

    def move_signature_file(self, id):
        """Move the Nparcel signature file to the staging directory for
        further processing.

        Move will only occur if a a staging directory exists.

        Filename is constructed on the *id* provided.  *id* is typically
        the record id of the "job_item" table record.

        **Args:**
            id: file name identifier of the file to move

        """
        status = True

        log.info('Moving signature file for job_item.id: %d' % id)
        if self.staging_dir is not None:
            # Define the signature filename.
            if self.signature_dir is not None:
                sig_file = os.path.join(self.signature_dir, "%d.ps" % id)
                if not os.path.exists(sig_file):
                    log.error('Cannot locate signature file: "%s"' %
                              sig_file)
                    status = False
            else:
                log.error('Signature directory is not defined')
                status = False

            if status:
                if os.path.exists(sig_file):
                    target = os.path.join(self.staging_dir, "%d.ps" % id)
                    log.info('Moving signature file "%s" to "%s"' %
                                (sig_file, target))
                    try:
                        os.rename(sig_file, target)
                    except OSError, e:
                        log.error('Signature file move failed: "%s"' % e)
                else:
                    log.error('Signature file "%s" does not exist' %
                              sig_file)
                    status = False
        else:
            status = False
            log.error('Skip file "%s" move: no staging directory' %
                      self.staging_dir)

        return status

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
        m = re.match('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d*',
                     row_list[2])
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

        self._create_dir(dir)

        if status:
            # Create the output file.
            time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            file = "%s_%s_%s_%s.txt.tmp" % ('VIC', 'VANA', 'REP', time)
            file_path = os.path.join(dir, file)
            try:
                log.info('Opening file "%s"' % file_path)
                fh = open(file_path, 'wb')
            except IOError, err:
                status = False
                log.error('Could not open out file "%s": %s')

        return fh

    def _create_dir(self, dir):
        """Helper method to manage the creation of the Exporter
        out directory.

        **Args:**
            dir: the name of the directory structure to create.

        """
        # Attempt to create the staging directory if it does not exist.
        if dir is not None and not os.path.exists(dir):
            try:
                log.info('Creating staging directory "%s"' % dir)
                os.makedirs(dir)
            except OSError, err:
                status = False
                log.error('Unable to create staging directory "%s": %s"' %
                            (dir, err))

    def _update_status(self, id):
        """Set the job_item.extract_ts column of record *id* to the
        current date/time.

        **Args:**
            id: the job_item.id column value to update.

        """
        time = self.db.date_now()

        log.info('Updating extracted timestamp for job_item.id')
        sql = self.db.jobitem.upd_collected_sql(id, time)
        self.db(sql)
