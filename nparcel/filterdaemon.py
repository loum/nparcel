__all__ = [
    "FilterDaemon",
]
import signal
import time
import os
import re

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import (check_eof_flag,
                                 get_directory_files,
                                 check_filename,
                                 create_dir,
                                 move_file,
                                 remove_files)


class FilterDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.Filter` class.

    .. attribute:: file_format

        :mod:`re` format string to match filter files against

    .. attribute:: staging_base

        base directory for outbound processing

    .. attribute:: customer

        context of outbound processing (default ``parcelpoint``)

    .. attribute:: filtering_rules

        list of tokens to match against the start of the agent code field

    .. attribute:: in_dirs

        list of inbound directory to check for files to process

    """
    _file_format = 'T1250_TOL.*\.txt'
    _staging_base = os.curdir
    _customer = 'parcelpoint'
    _filtering_rules = ['P', 'R']
    _in_dirs = ['/data/nparcel/aggregate']

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

        try:
            if self.config.staging_base is not None:
                self.set_staging_base(self.config.staging_base)
        except AttributeError, err:
            msg = ('Staging base not defined in config -- using %s' %
                   self.staging_base)
            log.info(msg)

        try:
            if self.config.filter_customer is not None:
                self.set_customer(self.config.filter_customer)
        except AttributeError, err:
            msg = ('Filter customer not defined in config -- using %s' %
                   self.customer)
            log.info(msg)

        try:
            if len(self.config.filtering_rules):
                self.set_filtering_rules(self.config.filtering_rules)
        except AttributeError, err:
            msg = ('Daemon filter rules not defined in config -- using %s' %
                   self.filtering_rules)
            log.info(msg)

        try:
            if self.config.aggregator_dirs is not None:
                self.set_in_dirs(self.config.aggregator_dirs)
        except AttributeError, err:
            msg = ('Inbound directory not defined in config -- using %s' %
                    self.in_dirs)
            log.info(msg)

        try:
            if self.config.support_emails is not None:
                self.set_support_emails(self.config.support_emails)
        except AttributeError, err:
            msg = ('Support emails not defined in config -- using %s' %
                    str(self.support_emails))
            log.info(msg)

    @property
    def file_format(self):
        return self._file_format

    def set_file_format(self, value):
        self._file_format = value

    @property
    def staging_base(self):
        return self._staging_base

    def set_staging_base(self, value):
        self._staging_base = value

    @property
    def customer(self):
        return self._customer

    def set_customer(self, value):
        self._customer = value

    @property
    def filtering_rules(self):
        return self._filtering_rules

    def set_filtering_rules(self, values):
        del self._filtering_rules[:]
        self._filtering_rules = []

        if values is not None:
            self._filtering_rules.extend(values)
            log.debug('Set filtering_rules to "%s"' %
                      str(self._filtering_rules))

    @property
    def in_dirs(self):
        return self._in_dirs

    def set_in_dirs(self, values):
        del self._in_dirs[:]
        self._in_dirs = []

        if values is not None and len(values):
            self._in_dirs.extend(values)
            log.debug('Set inbound directories "%s"' % str(self._in_dirs))

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

        filter = nparcel.Filter(rules=self.filtering_rules)

        commit = True
        if self.dry:
            commit = False

        while not event.isSet():
            fhs = {}
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
                        filtered_status = filter.process(line)
                        self.reporter(filtered_status)
                        if filtered_status:
                            self.write(line, fhs, file, dry=self.dry)
                f.close()
                self.close(fhs)

                if status and eof_found:
                    log.info('%s processing OK.' % file)
                    alerts = list(filter.alerts)
                    filter.set_alerts(None)
                    stats = self.reporter.report()
                    log.info(stats)
                    if not self.dry:
                        remove_files(file)

                    if len(alerts):
                        alert_table = self.create_table(alerts)
                        del alerts[:]
                        data = {'file': file,
                                'facility': self.__class__.__name__,
                                'err_table': alert_table}
                        self.emailer.send_comms(template='proc_err',
                                                data=data,
                                                recipients=self.support_emails,
                                                dry=self.dry)
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

    def get_files(self, dirs=None):
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
        if dirs is not None:
            dirs_to_check.extend(dirs)
        else:
            dirs_to_check.extend(self.in_dirs)

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

    def get_outbound_file(self, file, dir=None):
        """Generates the path to the outbound file resource for output
        of *file* processing.

        Generation of the outbound file is based on:

        * :attr:`nparcel.b2cconfig.staging_base` attribute (or current
          directory if not identified)

        * :attr:`nparcel.b2cconfig.filter_customer` (or *parcelpoint*
          if not identified)

        * *file* name (with ``.tmp`` appended)

        **Args:**
            *file*: the name of the T1250 file currently under processing
            control

        **Kwargs:**
            *dir*: override the :attr:`nparcel.b2cconfig.staging_base`

        **Returns:**
            the path and filename to the appropriate outbound file
            resource

        """
        log.info('Generating the outbound file resource for %s' % file)
        outbound_file_name = None

        if dir is not None:
            log.info('Setting staging base to "%s"' % dir)
            self.set_staging_base(dir)

        file_basename = os.path.basename(file)
        outbound_dir = os.path.join(self.staging_base, self.customer, 'out')

        if create_dir(outbound_dir):
            outbound_file_name = os.path.join(outbound_dir,
                                            file_basename + '.tmp')

        log.info('Outbound file resource name "%s"' % outbound_file_name)

        return outbound_file_name

    def write(self, data, fhs, infile, dry=False):
        """Write out *data* to the associated *fhs* file handler.

        *fhs* is based on the return value from
        :meth:`nparcel.FilterDaemon.get_outbound_file`

        **Args:**
            *data*: the line item to write out

            *fhs*: dictionary structure capturing open file handle objects

        """
        log.debug('Writing out data "%s ..."' % data[0:20])

        infile_basename = os.path.basename(infile)
        fh = fhs.get(infile_basename)
        if fh is None:
            log.info('Preparing file handler for infile %s' %
                     infile_basename)
            if not dry:
                outfile = self.get_outbound_file(infile)
                fhs[infile_basename] = open(outfile, 'w')
                fh = fhs[infile_basename]

        if not dry:
            fh.write('%s\n' % data)

    def close(self, fhs):
        """Closes out open T1250-specific file handles.

        Prepends the special end of file delimiter string '%%EOF'

        Renames the temporary writable file to T1250 format that can
        be consumed by the loader.

        **Args:**
            *fhs*: dictionary structure capturing open file handle objects

        **Returns:**
            list of files successfully closed

        """
        log.info('Closing out filtered file ...')
        files_closed = []

        filenames = []
        for k, fh in fhs.iteritems():
            filename = fh.name
            file = os.path.basename(filename)
            fh.write('%%EOF\r\n')
            fh.close()
            filenames.append(k)

            # ... and finally convert to T1250-proper.
            source = filename
            target = re.sub('\.tmp$', '', source)
            if move_file(source, target):
                files_closed.append(target)

        for f in filenames:
            del fhs[f]

        return files_closed
