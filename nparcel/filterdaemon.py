__all__ = [
    "FilterDaemon",
]
import signal
import time

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import (check_eof_flag,
                                 get_directory_files,
                                 check_filename)


class FilterDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.Filter` class.

    .. attribute:: file_format

        the :mod:`re` format string to match filter files against

    """
    _file_format = 'T1250_TOL.*\.txt'

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config='nparcel.conf'):
        super(FilterDaemon, self).__init__(pidfile=pidfile,
                                           file=file,
                                           dry=dry,
                                           batch=batch)

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

        try:
            if self.config.filter_loop is not None:
                self.set_loop(self.config.filter_loop)
        except AttributeError, err:
            log.info('Daemon loop not defined in config -- default %d sec' %
                     self.loop)

        try:
            if self.config.t1250_file_format is not None:
                self.set_file_format(self.config.t1250_file_format)
        except AttributeError, err:
            msg = ('Inbound file format not defined in config -- using %s' %
                   self.file_format)
            log.info(msg)

    @property
    def file_format(self):
        return self._file_format

    def set_file_format(self, value):
        self._file_format = value

    def _start(self, event):
        """Override the :method:`nparcel.utils.Daemon._start` method.

        Will perform a single iteration if the :attr:`file` attribute has
        a list of filenames to process.  Similarly, dry and batch modes
        only cycle through a single iteration.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        filter = nparcel.Filter()

        commit = True
        if self.dry:
            commit = False

        while not event.isSet():
            files = []
            if self.file is not None:
                files.append(self.file)
                event.set()
            else:
                files.extend(self.get_files())

            for file in files:
                log.info('Processing file: "%s" ...' % file)
                status = False

                try:
                    f = open(file, 'r')
                except IOError, e:
                    # TODO -- probably want to move file aside and send
                    # failure comms.
                    log.error('File open error "%s": %s' % (file, str(e)))
                    continue

                self.reporter.reset(identifier=file)
                eof_found = False
                for line in f:
                    record = line.rstrip('\r\n')
                    if record == '%%EOF':
                        log.info('EOF found')
                        status = True
                        eof_found = True
                        break
                    else:
                        self.reporter(filter.process(line))

                f.close()

                if status:
                    log.info('%s processing OK.' % file)
                    stats = self.reporter.report()
                    log.info(stats)
                else:
                    log.error('%s processing failed.' % file)
                    if not eof_found:
                        log.error("%s - %s" % ('File closed before EOF',
                                               'all line items ignored'))

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.loop)

    def get_files(self, dir=None):
        """Checks inbound directories (defined by the
        :attr:`nparcel.b2cconfig.aggregator_dir` config option) for valid
        T1250 files to be processed.  In this context, valid is interpreted
        as:
        * T1250 files that conform to the T1250 syntax

        **Args:**
            *dir*: directory to search (override the value defined in the
            configuration file)

        **Returns:**
            list of fully qualified and sorted (oldest first) T1250 files
            to be processed

        """
        files_to_process = []

        dirs_to_check = []
        if dir is not None:
            dirs_to_check.append(dir)
        else:
            try:
                dirs_to_check = [self.config.aggregator_dir]
            except AttributeError, err:
                log.info('Aggregator directory not defined in config')

        for dir_to_check in dirs_to_check:
            log.info('Looking for files at: %s ...' % dir_to_check)
            for file in get_directory_files(dir_to_check):
                if (check_filename(file, self.file_format) and
                    check_eof_flag(file)):
                    log.info('Found file: "%s" ' % file)
                    files_to_process.append(file)

        files_to_process.sort()
        log.debug('Files set to be processed: "%s"' % str(files_to_process))

        return files_to_process
