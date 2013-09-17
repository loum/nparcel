__all__ = [
    "LoaderDaemon",
]
import os
import re
import time
import datetime
import fnmatch
import signal

import nparcel
from nparcel.utils.log import log


class LoaderDaemon(nparcel.utils.Daemon):

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 config='nparcel.conf'):
        super(LoaderDaemon, self).__init__(pidfile=pidfile)

        self.file = file
        self.dry = dry

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

    def _start(self, event):
        signal.signal(signal.SIGTERM, self._exit_handler)

        sms_api = {'api': self.config.rest.get('sms_api'),
                   'api_username': self.config.rest.get('sms_user'),
                   'api_password': self.config.rest.get('sms_pw')}
        email_api = {'api': self.config.rest.get('email_api'),
                     'api_username': self.config.rest.get('email_user'),
                     'api_password': self.config.rest.get('email_pw'),
                     'support': self.config.rest.get('failed_email')}
        loader = nparcel.Loader(db=self.config.db_kwargs(),
                                proxy=self.config.proxy_string(),
                                scheme=self.config.rest.get('sms_scheme'),
                                sms_api=sms_api,
                                email_api=email_api)
        reporter = nparcel.Reporter()
        emailer = nparcel.Emailer()
        np_support = self.config.support_emails

        commit = True
        if self.dry:
            commit = False

        while not event.isSet():
            subject = ('Nploaderd processing error: %s' %
                       datetime.datetime.now().strftime("%Y/%m/%d %H:%M"))

            files = []
            if loader.db():
                if self.file is not None:
                    # Only makes sense to do one iteration if a single
                    # file has been given on the command line.
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
                reporter.reset(identifier=file)
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
                        reporter(loader.process(file_timestamp,
                                                record,
                                                bu_id,
                                                condition_map,
                                                self.dry))
                f.close()

                if not status and not eof_found:
                    log.error("%s - %s" % ('File closed before EOF found',
                                           'all line items ignored'))

                # Report the results.
                if status:
                    log.info('%s processing OK.' % file)
                    alerts = list(loader.alerts)
                    loader.reset(commit=commit)
                    if not self.dry and self.file is None:
                        self.archive_file(file)

                    # Report.
                    reporter.end()
                    stats = reporter.report()
                    log.info(stats)
                    if reporter.bad_records > 0:
                        msg = ("%s\n\n%s" % (stats, "\n".join(alerts)))
                        del alerts[:]

                        emailer.set_recipients(np_support)
                        emailer.send(subject=subject, msg=msg, dry=self.dry)
                else:
                    log.error('%s processing failed.' % file)

            if not event.isSet():
                # Only makes sense to do one iteration of a dry run.
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config.loader_loop)

    def _exit_handler(self, signal, frame):
        log_msg = '%s --' % type(self).__name__
        log.info('%s SIGTERM intercepted' % log_msg)
        self.set_exit_event()

    def get_files(self):
        """
        """
        files_to_process = []

        for dir in self.config.in_dirs:
            log.info('Looking for files at: %s ...' % dir)
            for file in self.files(dir):
                if self.check_filename(file) and self.check_eof_flag(file):
                    log.info('Found file: "%s" ' % file)

                    # Check that it's not in the archive already.
                    archive_path = self.get_customer_archive(file)
                    if (archive_path is not None and
                        os.path.exists(archive_path)):
                        log.error('File %s is archived' % file)
                    else:
                        files_to_process.append(file)

        files_to_process.sort()
        log.debug('Files set to be processed: "%s"' % str(files_to_process))

        return files_to_process

    def files(self, path):
        try:
            for file in os.listdir(path):
                file = os.path.join(path, file)
                if os.path.isfile(file):
                    yield file
        except OSError, err:
            log.error(err)

    def check_filename(self, file):
        """Parse filename string supplied by *file* and check that it
        conforms to the Nparcel format.

        Nparcel format is based T1250_TOLc_xxx_yyyymmddhhmmss.txt where:

        * c is the Business Unit name ('P' for Priority etc.)

        * xxx is the optional state ('VIC' for Victoria etc.)

        * yyyymmddhhmmss is the time the file was generated

        **Args:**
            file: the filename string

        **Returns:**
            boolean ``True`` if filename string conforms to Nparcel format

            boolean ``False`` otherwise

        """
        status = False

        if fnmatch.fnmatch(os.path.basename(file), 'T1250_TOL*.txt'):
            status = True
        else:
            log.error('Filename "%s" did not match filtering rules' % file)

        return status

    def check_eof_flag(self, file):
        """
        """
        status = False

        fh = open(file, 'r')
        fh.seek(-7, 2)
        eof_search = fh.readline()
        fh.close()

        eof_search = eof_search.rstrip('\r\n')
        if eof_search == '%%EOF':
            log.debug('File "%s" EOF found' % file)
            status = True
        else:
            log.debug('File "%s" EOF NOT found' % file)

        return status

    def validate_file(self, filename):
        """Parse the Nparcel-format filename string and attempt to extract
        the Business Unit and file timestamp.

        **Kwargs:**
            filename: the filename string to parse

        *Returns:**
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
        """
        """
        archive_path = self.get_customer_archive(file)
        archive_base = os.path.dirname(archive_path)

        log.info('Archiving "%s" to "%s"' % (file, archive_path))

        if not os.path.exists(archive_base):
            log.info('Creating archive directory: %s' % archive_base)
            os.makedirs(archive_base)

        log.info('Rename: %s to %s' % (file, archive_path))
        try:
            os.rename(file, archive_path)
        except OSError, err:
            log.error('Rename: %s to %s failed -- %s' % (file,
                                                         archive_path,
                                                         err))
            pass

    def get_customer_archive(self, file):
        customer = self.get_customer(file)
        filename = os.path.basename(file)
        archive_dir = None
        m = re.search('T1250_TOL.*_(\d{8})\d{6}\.txt', filename)
        if m is not None:
            file_timestamp = m.group(1)
            dir = os.path.join(self.config.archive_dir,
                               customer,
                               file_timestamp)
            archive_dir = os.path.join(dir, filename)

        return archive_dir

    def get_customer(self, file):
        """
        """
        dirname = os.path.dirname(file)
        (head, customer) = os.path.split(os.path.dirname(dirname))

        return customer
