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
          'IDENTITY_DATA',
          'ITEM_NBR']


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
        self._headers = []

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

    @property
    def headers(self):
        return self._headers

    def set_headers(self, values):
        del self._headers[:]

        if values is not None:
            self._headers.extend(values)

    def get_out_directory(self, business_unit):
        """Uses the *business_unit* name to construct the output directory
        to which the report and signature files will be placed for further
        processing.

        Staging directories are based on the Business Unit.  For example,
        the Business Unit "Priority" will create the directory
        ``priority/out`` off the base staging directory.

        Will check if the output directory structure exists before
        attempting to create it.

        **Args:**
            business_unit: name of the Business Unit that is associated
            with the collected items output files.

        **Returns:**
            fully qualified name of the output directory if it exists and
            is accessible.  ``None`` otherwise.

        """
        log.info('Checking output directory for "%s" ...' % business_unit)
        try:
            out_dir = os.path.join(self.staging_dir,
                                   business_unit.lower(),
                                   'out')
            self._create_dir(out_dir)
        except AttributeError, err:
            log.error('Output directory error: "%s"' % err)
            out_dir = None

        return out_dir

    def get_collected_items(self, business_unit_id):
        """Query DB for recently collected items.

        **Args:**
            business_unit_id: business_unit.id

        """
        log.info('Searching for collected items ...')
        sql = self.db.jobitem.collected_sql(business_unit=business_unit_id)
        self.db(sql)

        # Get the query headers.
        self.set_headers(self.db.columns())

        for row in self.db.rows():
            cleansed_row = self._cleanse(row)
            self._collected_items.append(cleansed_row)

        log.info('Collected items: %d' % len(self._collected_items))

    def process(self, business_unit_id, out_dir, dry=False):
        """
        """
        valid_items = []

        self.get_collected_items(business_unit_id)

        for row in self._collected_items:
            job_item_id = row[1]

            # Attempt to move the signature file.
            if self.move_signature_file(job_item_id, out_dir, dry=dry):
                log.info('job_item.id: %d OK' % job_item_id)
                valid_items.append(row)
            else:
                log.error('job_item.id: %d failed' % job_item_id)

        return valid_items

    def move_signature_file(self, id, out_dir, dry=False):
        """Move the Nparcel signature file to the staging directory for
        further processing.

        Move will only occur if a a staging directory exists.

        Filename is constructed on the *id* provided.  *id* is typically
        the record id of the "job_item" table record.

        **Args:**
            id: file name identifier of the file to move

        **Kwargs:**
            dry: only report what would happen (do not move file)

        **Returns:**
            boolean ``True`` if the signature file is located successfully
            and moved into the staging *out_dir*

            boolean ``False`` otherwise

        """
        status = True

        log.info('Moving signature file for job_item.id: %d' % id)
        # Define the signature filename.
        if self.signature_dir is not None:
            sig_file = os.path.join(self.signature_dir, "%d.ps" % id)
            if not os.path.exists(sig_file):
                log.error('Cannot locate signature file: "%s"' % sig_file)
                status = False
        else:
            log.error('Signature directory is not defined')
            status = False

        if status:
            if os.path.exists(sig_file):
                target = os.path.join(out_dir, "%d.ps" % id)
                log.info('Moving signature file "%s" to "%s"' %
                         (sig_file, target))
                try:
                    if not dry:
                        os.rename(sig_file, target)
                except OSError, e:
                    log.error('Signature file move failed: "%s"' % e)
                    status = False
            else:
                log.error('Signature file "%s" does not exist' % sig_file)
                status = False

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
        # Handle sqlite and MSSQL dates differently.
        pickup_ts = row[2]
        if isinstance(row[2], str):
            m = re.match('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d*',
                        row[2])
            try:
                pickup_ts = m.group(1)
            except AttributeError, err:
                log.error('Error cleansing pickup_ts "%s": %s' % (row[2],
                                                                  err))
        elif isinstance(row[2], datetime.datetime):
            pickup_ts = row[2].strftime("%Y-%m-%d %H:%M:%S")

        log.debug('Cleansed pickup_ts produced "%s"' % pickup_ts)

        row_list[2] = pickup_ts

        return tuple(row_list)

    def report(self, items, out_dir=None):
        """Cycle through the newly identified collected items and produce
        a report.

        Once an entry is made in the report, also update the database
        so that it does not appear in future runs.

        **Returns:**
            name of the report file

        """
        file_name = None
        target_file = None

        if items:
            header = '|'.join(FIELDS)
            if out_dir is None:
                print(header)
                for item in items:
                    print('%s' % '|'.join(map(str, item)))
            else:
                fh = self.outfile(out_dir)
                file_name = fh.name
                fh.write('%s\n' % header)
                for item in items:
                    fh.write('%s\n' % '|'.join(map(str, item)))
                    job_item_id = item[1]
                    self._update_status(job_item_id)
                fh.close()

                # Rename the output file so that it's ready for delivery.
                target_file = file_name.replace('.txt.tmp', '.txt')
                log.info('Renaming out file to "%s"' % target_file)
                os.rename(file_name, target_file)

        else:
            log.info('No collected items to report')

        return target_file

    def get_header(self, sequence=None):
        """Generate the exporter report header.

        Provide a tuple *sequence* to control the items displayed and their
        order.

        **Args:**
            sequence: tuple of values that represent the index of the
            fields that are returned by the job_item.collected_sql() query.
            For example:

                (0, 1, 4, 5, 2, 3)

        **Returns:**
            The exporter report header as a string if pipe delimited
            column names

        """
        log.debug('Generating exporter header')
        headers = "|".join(self.headers)
        if sequence is not None and isinstance(sequence, tuple):
            try:
                headers = "|".join([self.headers[i] for i in sequence])
            except IndexError, err:
                log.warn('Default header generated: %s' % err)
        else:
            log.debug('Sequence not a tuple -- default header generated')

        return headers

    def outfile(self, dir):
        """Creates the Exporter output file based on current timestamp
        and verifies creation at the staging directory *dir*.

        During output file access, prepends ``.tmp`` to the file.

        **Args:**
            dir: base directory name of the staging directory

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

        **Returns:**
            boolean ``True`` if directory exists.

            boolean ``False`` if the directory does not exist and the
            attempt to create it fails.

        """
        status = True

        # Attempt to create the staging directory if it does not exist.
        if dir is not None and not os.path.exists(dir):
            try:
                log.info('Creating directory "%s"' % dir)
                os.makedirs(dir)
            except OSError, err:
                status = False
                log.error('Unable to create directory "%s": %s"' %
                          (dir, err))

        return status

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
        self.db.commit()

    def reset(self):
        """Initialise object state in readiness for another iteration.
        """
        del self._collected_items[:]
        del self._headers[:]
