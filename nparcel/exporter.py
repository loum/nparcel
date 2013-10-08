__all__ = [
   "Exporter",
]
import re
import os
import datetime
import operator

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import create_dir

STATES = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'ACT']


class Exporter(object):
    """Nparcel Exporter.

    .. attribute:: archive_dir

        where to archive signature files (if not being transfered).
        Default of ``None`` will not archive files.

    """

    def __init__(self,
                 db=None,
                 signature_dir=None,
                 staging_dir=None,
                 archive_dir=None):
        """Exporter object initialiser.
        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self._signature_dir = signature_dir
        self._staging_dir = staging_dir
        create_dir(self._staging_dir)
        self._archive_dir = archive_dir
        create_dir(self._archive_dir)

        self._out_dir = None

        self._collected_items = []
        self._header = ()

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

        create_dir(dir=self._staging_dir)

    @property
    def out_dir(self):
        return self._out_dir

    def set_out_dir(self, business_unit):
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

        """
        if business_unit is None:
            self._out_dir = None
        else:
            log.info('Checking output directory for "%s" ...' % business_unit)
            try:
                self._out_dir = os.path.join(self.staging_dir,
                                             business_unit.lower(),
                                             'out')
                create_dir(self._out_dir)
            except AttributeError, err:
                log.error('Output directory error: "%s"' % err)
                self._out_dir = None

    @property
    def archive_dir(self):
        return self._archive_dir

    def set_archive_dir(self, value):
        self._archive_dir = value

        if self._archive_dir is not None:
            if not create_dir(self._archive_dir):
                self._archive_dir = None

    @property
    def header(self):
        return self._header

    def set_header(self, values):
        self._header = ()

        if values is not None:
            self._header = values

    def get_collected_items(self, business_unit_id):
        """Query DB for recently collected items.

        **Args:**
            business_unit_id: business_unit.id

        """
        log.info('Searching for collected items ...')
        sql = self.db.jobitem.collected_sql(business_unit=business_unit_id)
        self.db(sql)

        # Get the query header.
        self.set_header(self.db.columns())

        for row in self.db.rows():
            cleansed_row = self._cleanse(row)
            self._collected_items.append(cleansed_row)

        log.info('Collected items: %d' % len(self._collected_items))

    def process(self,
                business_unit_id,
                file_control={'ps': True},
                dry=False):
        """
        Identifies picked up items and prepares reporting.

        Moves/archives signature files as defined by *file_control*.

        **Args:**
            business_unit_id: the Business Unit id as per "business_unit.id"
            column

            signature files will be deposited to.

        **Kwargs:**
            file_control: dictionary structure which controls whether the
            file extension type is moved or archived.  For example, the
            following structure sets '.ps' file extensions to be moved to
            the :attr:`out_dir` whilst ``*.png`` are moved to the
            :attr:`archive_dir`::

                {'ps': True,
                 'png': False}

            Defaults to ``None`` in which case only ``*.ps`` files are moved
            to the :attr:`out_dir`.

            dry: only report what would happen (do not move file)

        """
        valid_items = []

        self.get_collected_items(business_unit_id)

        for row in self._collected_items:
            job_item_id = row[1]

            # Attempt to move the signature file.
            for extension, send_to_out_dir in file_control.iteritems():
                if send_to_out_dir:
                    target_dir = self.out_dir
                else:
                    target_dir = self.archive_dir

                if target_dir is not None:
                    if self.move_signature_file(job_item_id,
                                                target_dir,
                                                extension,
                                                file_control,
                                                dry):
                        log.info('job_item.id: %d OK' % job_item_id)
                        # Only tag file sent to out_dir.
                        if send_to_out_dir:
                            valid_items.append(row)
                    else:
                        log.error('job_item.id: %d failed' % job_item_id)

        return valid_items

    def move_signature_file(self,
                            id,
                            out_dir,
                            extension='ps',
                            file_control={'ps': True},
                            dry=False):
        """Move the Nparcel signature file to the staging directory for
        further processing.

        .. note::

            Move will only occur if a a staging directory exists.

        Filename is constructed on the *id* provided.  *id* is typically
        the record id of the "job_item" table record.

        **Args:**
            *id*: file name identifier of the file to move

            *out_dir*: target directory

            *extension*: the extension of the filename to move
            (default '.ps')

        **Kwargs:**
            *dry*: only report what would happen (do not move file)

        **Returns:**
            boolean ``True`` if the signature file is located successfully
            and moved into the staging *out_dir*

            boolean ``False`` otherwise

        """
        log.info('Moving signature file for job_item.id: %d' % id)
        status = True

        # Define the signature filename.
        if self.signature_dir is None:
            log.error('Signature directory is not defined')
            status = False

        if status:
            sig_file = os.path.join(self.signature_dir,
                                    "%d.%s" % (id, extension))

            if not os.path.exists(sig_file):
                log.error('Cannot locate signature file: "%s"' % sig_file)
                status = False
            else:
                target = os.path.join(out_dir, "%d.%s" % (id, extension))
                log.info('Moving signature file "%s" to "%s"' %
                         (sig_file, target))
                try:
                    if not dry:
                        os.rename(sig_file, target)
                except OSError, e:
                    log.error('Signature file move failed: "%s"' % e)
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
                log.error('Cannot cleanse pickup_ts "%s": %s' % (row[2], err))
        elif isinstance(row[2], datetime.datetime):
            pickup_ts = row[2].strftime("%Y-%m-%d %H:%M:%S")
        log.debug('Cleansed pickup_ts: "%s"' % pickup_ts)
        row_list[2] = pickup_ts

        # Get rid of spaces around the state.
        try:
            row_list[8] = row_list[8].strip()
            log.debug('Cleansed state: "%s"' % row_list[8])
        except (IndexError, AttributeError), err:
            log.warn('Cleansed state -- no value: %s' % err)

        return tuple(row_list)

    def report(self,
               items,
               sequence=None,
               identifier='P',
               state_reporting=False):
        """Cycle through the newly identified collected items and produce
        a report.

        Once an entry is made in the report, also update the database
        so that it does not appear in future runs.

        **Args:**
            items: list of report line item tuples

        **Kwargs:**
            sequence: business unit-based report column control

            identifier: business unit specific file identifier

            state_reporting: Business Unit reporting is output to separate
            files based on Agent state

        **Returns:**
            list of report file names that are generated

        """
        file_name = None

        target_files = []
        if not items:
            log.info('No collected items to report')
        else:
            index = self.get_header_column('JOB_KEY')
            sorted_items = sorted(items,
                                  key=operator.itemgetter(index),
                                  cmp=lambda x, y: int(x) - int(y))

            rpts = {}
            if state_reporting:
                log.debug('Reporting set to state based')
                state_col = self.get_header_column('AGENT_STATE')

                # Hardwired Fast fugliness.
                nt_rows = [r for r in sorted_items if r[state_col] == 'NT']
                tas_rows = [r for r in sorted_items if r[state_col] == 'TAS']

                for state in STATES:
                    log.debug('Reporting on state: %s' % state)
                    rows = [r for r in sorted_items if r[state_col] == state]

                    # Typical Fast fugliness, certain states tack onto others.
                    if state == 'VIC':
                        rows += tas_rows
                    if state == 'SA':
                        rows += nt_rows

                    log.debug('State row count: %d' % len(rows))
                    rpts[state] = {'id': identifier,
                                   'items': rows}
            else:
                # Just one report -- and it's the default name.
                rpts['VIC'] = {'id': identifier,
                               'items': sorted_items}

            for state, v in rpts.iteritems():
                if v.get('items') is not None and len(v.get('items')):
                    out_file = self.dump_report_output(v.get('items'),
                                                    sequence,
                                                    identifier,
                                                    state)
                    if out_file is not None:
                        target_files.append(out_file)

        return target_files

    def dump_report_output(self,
                           sorted_items,
                           sequence,
                           identifier,
                           state='VIC'):
        """
        """
        target_file = None

        header = self.get_report_line(self.header, sequence)
        if self.out_dir is None:
            print(header)
            for item in sorted_items:
                print('%s' % (self.get_report_line(item, sequence)))
        else:
            fh = self.outfile(self.out_dir, identifier, state)
            file_name = fh.name
            fh.write('%s\n' % header)
            for item in sorted_items:
                fh.write('%s\n' % self.get_report_line(item, sequence))
                job_item_id = item[1]
                self._update_status(job_item_id)
            fh.close()

            # Rename the output file so that it's ready for delivery.
            target_file = file_name.replace('.txt.tmp', '.txt')
            log.info('Renaming out file to "%s"' % target_file)
            os.rename(file_name, target_file)

        return target_file

    def get_report_line(self, line, sequence=None):
        """Generate the exporter report line entry.

        Provide a tuple *sequence* to control the items displayed and their
        order.

        **Args:**
            line: tuple of the collected item record as per the output from
            the job_item.collected_item() SQL

            sequence: tuple of values that represent the index of the
            fields that are returned by the job_item.collected_sql() query.
            For example:

                (0, 1, 4, 5, 2, 3)

        **Returns:**
            The exporter report header as a string if pipe delimited
            column names

        """
        report_line = "|".join(map(str, line))
        if sequence is None or not len(sequence):
            log.debug('Sequence not defined -- default line generated')
        else:
            seq = sequence
            if not isinstance(sequence, tuple):
                seq = (int(x) for x in sequence.replace(' ', '').split(','))

            try:
                report_line = "|".join(map(str, [line[i] for i in seq]))
            except IndexError, err:
                log.warn('Default report line entry generated: %s' % err)

        return report_line

    def outfile(self, dir, identifier, state='VIC'):
        """Creates the Exporter output file based on current timestamp
        and verifies creation at the staging directory *dir*.

        During output file access, prepends ``.tmp`` to the file.

        **Args:**
            dir: base directory name of the staging directory

            identifier: business unit specific file identifier

        **Returns:**
            open file handle to the exporter report file (or None if file
            access fails)

        """
        status = True
        fh = None

        create_dir(dir)

        if status:
            # Create the output file.
            time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            file = ("%s_%s_%s%s_%s.txt.tmp" %
                    (state, 'VANA', 'RE', identifier, time))
            file_path = os.path.join(dir, file)
            try:
                log.info('Opening file "%s"' % file_path)
                fh = open(file_path, 'wb')
            except IOError, err:
                status = False
                log.error('Could not open out file "%s": %s')

        return fh

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

    def get_header_column(self, column_name):
        """Bit of a hard-wired fudge which just returns the list index
        of the *column_name* column.

        **Args:**
            column_name: name of column as per the exporter headers.  For
            example, 'JOB_KEY'

        **Returns:**
            integer value representing the index of the 'JOB_KEY' column
            or 0 if *column_name* column is not found

        """
        index = 0

        try:
            index = list(self.header).index(column_name)
        except ValueError, err:
            log.warn('"%s" not in exporter header' % column_name)

        return index

    def reset(self):
        """Initialise object state in readiness for another iteration.
        """
        del self._collected_items[:]
        self._header = ()
        self._out_dir = None
