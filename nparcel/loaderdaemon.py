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

        self.config = nparcel.Config(file=config)

    def _start(self, event):
        signal.signal(signal.SIGTERM, self._exit_handler)

        loader = nparcel.Loader(file_bu=self.config('file_bu'),
                                db=self.config.db_kwargs())
        reporter = nparcel.Reporter()

        commit = True
        if self.dry:
            commit = False

        while not event.isSet():
            if loader.db():
                files = []
                if self.file is not None:
                    files.append(self.file)
                else:
                    files.extend(self.get_files())

                for file in files:
                    log.info('Processing file: "%s" ...' % file)

                    status = False

                    try:
                        f = open(file, 'r')
                        file_timestamp = self.validate_file(file)

                        reporter.reset(identifier=file)
                        for line in f:
                            record = line.rstrip('\r\n')
                            if record == '%%EOF':
                                log.info('EOF found')
                                status = True
                            else:
                                reporter(loader.process(file_timestamp,
                                                        record))
                        f.close()

                    except IOError, e:
                        log.error('Error opening file "%s": %s' %
                                  (file, str(e)))

                    # Report the results.
                    if status:
                        log.info('%s processing OK.' % file)
                        loader.reset(commit=commit)
                        if not self.dry:
                            self.archive_file(file)

                        # Report.
                        reporter.end()
                        reporter.set_failed_log(loader.alerts)
                        reporter.report()
                    else:
                        log.error('%s processing failed.' % file)
            else:
                log.error('ODBC connection failure -- aborting')
                event.set()

            if not event.isSet():
                # Only makes sense to do one iteration of a dry run.
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config('loader_loop'))

    def _exit_handler(self, signal, frame):
        log_msg = '%s --' % type(self).__name__
        log.info('%s SIGTERM intercepted' % log_msg)
        self.set_exit_event()

    def get_files(self):
        """
        """
        files_to_process = []

        for dir in self.config('in_dirs'):
            log.info('Looking for files at: %s ...' % dir)
            for file in self.files(dir):
                if self.check_filename(file) and self.check_eof_flag(file):
                    log.info('Found file: "%s" ' % file)

                    # Check that it's not in the archive already.
                    archive_path = self.get_customer_archive(file)
                    if os.path.exists(archive_path):
                        log.error('File %s is archived' % file)
                    else:
                        files_to_process.append(file)

        files_to_process.sort()
        log.debug('Files set to be processed: "%s"' % str(files_to_process))

        return files_to_process

    def files(self, path):
        for file in os.listdir(path):
            file = os.path.join(path, file)
            if os.path.isfile(file):
                yield file

    def check_filename(self, file):
        """
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

    def validate_file(self, filename=None):
        """
        """
        log.debug('Validating filename: "%s"' % filename)
        m = re.search('T1250_TOL._(\d{14})\.txt', filename)
        file_timestamp = m.group(1)

        parsed_time = time.strptime(file_timestamp, "%Y%m%d%H%M%S")
        log.debug('parsed_time: %s' % parsed_time)
        dt = datetime.datetime.fromtimestamp(time.mktime(parsed_time))
        dt_formatted = dt.isoformat(' ')

        return dt_formatted

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
        m = re.search('T1250_TOL._(\d{8})\d{6}\.txt', filename)
        file_timestamp = m.group(1)

        archive_dir = os.path.join(self.config('archive_dir'),
                                               customer,
                                               file_timestamp)

        return os.path.join(archive_dir, filename)

    def get_customer(self, file):
        """
        """
        dirname = os.path.dirname(file)
        (head, customer) = os.path.split(os.path.dirname(dirname))

        return customer
