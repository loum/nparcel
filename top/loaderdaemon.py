__all__ = [
    "LoaderDaemon",
]
import os
import re
import time
import datetime
import signal

import top
from top.utils.log import log
from top.utils.files import (get_directory_files,
                             check_eof_flag,
                             move_file,
                             copy_file,
                             check_filename)


class LoaderDaemon(top.DaemonService):
    """Daemoniser facility for the :class:`top.Loader` class.

    .. attribute:: file_format

        the :mod:`re` format string to match loader files against

    .. attribute:: business_units

        dictionary of business units names and their bu_ids as per the
        business_units.id table column

    .. attribute:: comms_delivery_partners

        dictionary of Business Unit based list of Delivery Partners that
        will have comms event files created during the load process

    """
    _file_format = 'T1250_TOL.*\.txt'
    _business_units = {}
    _comms_delivery_partners = {}

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config='top.conf'):
        c = None
        if config is not None:
            c = top.B2CConfig(config)
        top.DaemonService.__init__(self,
                                   pidfile=pidfile,
                                   file=file,
                                   dry=dry,
                                   batch=batch,
                                   config=c)

        try:
            self.set_support_emails(self.config.support_emails)
        except AttributeError, err:
            msg = ('%s email.support not in config: %s. Using "%s"' %
                   (self.facility, err, self.support_emails))
            log.info(msg)

        try:
            self.set_business_units(self.config.business_units)
        except AttributeError, err:
            log.debug('%s business_units not in config: %s. Using "%s"' %
                      (self.facility, err, self.business_units))

        try:
            tmp = self.config.comms_delivery_partners
            self.set_comms_delivery_partners(tmp)
        except AttributeError, err:
            log.debug('%s %s not in config: %s. Using "%s"' %
                      (self.facility,
                       'comms_delivery_partners',
                       err,
                       self.comms_delivery_partners))

    @property
    def file_format(self):
        return self._file_format

    def set_file_format(self, value):
        self._file_format = value

    @property
    def comms_delivery_partners(self):
        return self._comms_delivery_partners

    def set_comms_delivery_partners(self, values):
        self._comms_delivery_partners.clear()

        if values is not None:
            self._comms_delivery_partners = values
        log.debug('%s comms_delivery_partners set to: "%s"' %
                  (self.facility, self._comms_delivery_partners))

    @property
    def business_units(self):
        return self._business_units

    def set_business_units(self, values=None):
        self._business_units.clear()

        if values is not None:
            self._business_units = values
        log.debug('%s business_units set to: "%s"' %
                  (self.facility, self.business_units))

    def _start(self, event):
        """Override the :method:`top.utils.Daemon._start` method.

        Will perform a single iteration if the :attr:`file` attribute has
        a list of filenames to process.  Similarly, dry and batch modes
        only cycle through a single iteration.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        loader = top.Loader(db=self.config.db_kwargs(),
                            comms_dir=self.config.comms_dir)
        commit = True
        if self.dry:
            commit = False

        while not event.isSet():
            files = []
            if loader.db():
                if self.file is not None:
                    files.append(self.file)
                    event.set()
                else:
                    files.extend(self.get_files())
            else:
                log.error('ODBC connection failure -- aborting')
                event.set()
                continue

            # Start processing files.
            for file in files:
                log.info('Processing file: "%s" ...' % file)
                status = False
                try:
                    f = open(file, 'r')
                except IOError, e:
                    log.error('File error "%s": %s' % (file, str(e)))
                    continue

                # We should have a file handle.
                self.reporter.reset(identifier=file)
                (bu, file_timestamp) = self.validate_file(file)
                if bu is None or file_timestamp is None:
                    log.error('Unable to validate file "%s":' % file)
                    continue

                bu_id = self.config.file_bu.get(bu.lower())
                if bu_id is None:
                    log.error('Unable to get a BU Id from "%s"' % bu)
                    continue

                bu_id = int(bu_id)
                condition_map = self.config.condition_map(bu)
                eof_found = False
                for line in f:
                    record = line.rstrip('\r\n')
                    if record == '%%EOF':
                        log.info('EOF found')
                        status = True
                        eof_found = True
                        break
                    else:
                        dps = self.get_comms_delivery_partners(bu_id)
                        self.reporter(loader.process(file_timestamp,
                                                     record,
                                                     bu_id,
                                                     condition_map,
                                                     dps,
                                                     dry=self.dry))
                f.close()

                if not status and not eof_found:
                    log.error("%s - %s" % ('File closed before EOF found',
                                           'all line items ignored'))

                # Report the results.
                if status and eof_found:
                    self.send_table(recipients=self.support_emails,
                                    table_data=list(loader.alerts),
                                    identifier=file,
                                    dry=self.dry)
                    loader.reset(commit=commit)

                    # Aggregate the files for further processing.
                    if not self.dry and self.file is None:
                        aggregate = condition_map.get('aggregate_files')
                        self.distribute_file(file, aggregate)

                    stats = self.reporter.report()
                    log.info(stats)
                else:
                    log.error('%s processing failed.' % file)

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config.loader_loop)

    def get_files(self):
        """Checks inbound directories (defined by the
        :attr:`top.b2cconfig.in_dirs` config option) for valid
        T1250 files to be processed.  In this context, valid is interpreted
        as:
        * T1250 files that conform to the T1250 syntax

        * have not already been archived

        * contain the T1250 EOF flag

        **Returns:**
            list of fully qualified and sorted (oldest first) T1250 files
            to be processed

        """
        files_to_process = []

        for dir in self.config.in_dirs:
            log.info('Looking for files at: %s ...' % dir)
            for file in get_directory_files(dir):
                if (check_filename(file, self.file_format) and
                    check_eof_flag(file)):
                    log.info('Found file: "%s" ' % file)
                    archive_path = self.get_customer_archive(file)
                    if (archive_path is not None and
                        os.path.exists(archive_path)):
                        log.error('File %s is archived' % file)
                    else:
                        files_to_process.append(file)

        files_to_process.sort()
        log.debug('Files set to be processed: "%s"' % str(files_to_process))

        return files_to_process

    def validate_file(self, filename):
        """Parse the T1250-format filename string and attempt to extract
        the Business Unit and file timestamp.

        **Kwargs:**
            filename: the filename string to parse

        **Returns:**
            tuple stucture as (<business_unit>, <timestamp>)

        """
        log.debug('Validating filename: "%s"' % filename)
        m = re.search('T1250_(TOL.*)_(\d{14})\.txt', filename)
        bu = None
        dt_formatted = None
        if m is None:
            log.error('Could not parse BU/time from file "%s"' % filename)
        else:
            bu = m.group(1).lower()
            file_timestamp = m.group(2)
            parsed_time = time.strptime(file_timestamp, "%Y%m%d%H%M%S")
            log.debug('parsed_time: %s' % parsed_time)
            dt = datetime.datetime.fromtimestamp(time.mktime(parsed_time))
            dt_formatted = dt.isoformat(' ')
            log.info('Parsed BU/time "%s/%s" from file "%s"' %
                     (bu, dt_formatted, filename))

        return (bu, dt_formatted)

    def archive_file(self, file):
        """Will attempt to move *file* to the Business Unit specific
        archive directory.

        **Args:**
            *file*: string representation of the filename to archive

        """
        log.info('Archiving "%s"' % file)
        archive_path = self.get_customer_archive(file)
        move_file(file, archive_path)

    def aggregate_file(self, file):
        """Will attempt to copy *file* to the special aggregator directory
        for further processing.

        **Args:**
            *file*: string representation of the filename to aggregate

        """
        log.info('Aggregating file "%s"' % file)
        if len(self.config.aggregator_dirs):
            for aggregator_dir in self.config.aggregator_dirs:
                aggregator_path = os.path.join(aggregator_dir,
                                               os.path.basename(file))
                copy_file(file, aggregator_path)

    def get_customer_archive(self, file):
        """Will determine the archive directory path based on the
        *file* name provided.

        **Args:**
            *file*: the T1250 file.  For example,
            ``T1250_TOLI_20130828202901.txt``

        **Returns:**
            string representing the archive path.  For example, for *file*
            ``T1250_TOLI_20130828202901.txt`` the resultant archive
            file path would be
            ``<archive_base>/ipec/20130828/T1250_TOLI_20130828202901.txt``

        """
        customer = self.get_customer(file)
        filename = os.path.basename(file)
        archive_filepath = None
        m = re.search('T1250_TOL.*_(\d{8})\d{6}\.txt', filename)
        if m is not None:
            file_timestamp = m.group(1)
            dir = os.path.join(self.config.archive_dir,
                               customer,
                               file_timestamp)
            archive_filepath = os.path.join(dir, filename)

        return archive_filepath

    def get_customer(self, file):
        """
        """
        dirname = os.path.dirname(file)
        (head, customer) = os.path.split(os.path.dirname(dirname))

        return customer

    def distribute_file(self, file, aggregate_file=False):
        """Helper method that manages post-processing file distribution.

        **Args:**
            *file*: the T1250 file.  For example,
            ``T1250_TOLI_20130828202901.txt``

            *aggregate_file*: boolean flag that manages the conditional
            copy of *file* to the aggregate directory for further
            processing.  The aggregate directory location is determined
            by the *aggregator* configuration option under the *dirs*
            section.

        """
        if aggregate_file:
            self.aggregate_file(file)

        self.archive_file(file)

    def get_comms_delivery_partners(self, bu_id):
        """Lookup of Delivery Partners associated with *bu_id* that should
        have comms sent.

        **Args:**
            *bu_id*: the Business Unit ID that typically relates to the
            business_unit.id table column

        **Returns**:
            list of Delivery Partners that are enabled to have comms event
            files triggered

        """
        dps = []

        # Get the business_unit key whose value is bu_id.
        # For duplicates, first in best dressed.
        bu_key = None
        for k, v in self.business_units.iteritems():
            if v == bu_id:
                bu_key = k.lower()
                break

        if bu_key is not None:
            if self.comms_delivery_partners.get(bu_key) is not None:
                dps = self.comms_delivery_partners.get(bu_key)

        log.debug('Delivery Partners for bu_id %d: "%s"' % (bu_id, dps))
        return dps
