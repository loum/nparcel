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
from nparcel.utils.setter import (set_scalar,
                                  set_list,
                                  set_dict)


class FilterDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.Filter` class.

    .. attribute:: *file_format*

        :mod:`re` format string to match filter files against

    .. attribute:: *filters*

        list of tokens to match against the start of the agent code field

    .. attribute:: *in_dirs*

        list of inbound directory to check for files to process

    """
    _file_format = 'T1250_TOL.*\.txt'
    _staging_base = os.curdir
    _filters = {}
    _in_dirs = []

    @property
    def file_format(self):
        return self._file_format

    @set_scalar
    def set_file_format(self, value):
        pass

    @property
    def staging_base(self):
        return self._staging_base

    @set_scalar
    def set_staging_base(self, value):
        pass

    @property
    def filters(self):
        return self._filters

    @set_dict
    def set_filters(self, values=None):
        pass

    @property
    def in_dirs(self):
        return self._in_dirs

    @set_list
    def set_in_dirs(self, values=None):
        pass

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config=None):
        nparcel.DaemonService.__init__(self,
                                       pidfile=pidfile,
                                       file=file,
                                       dry=dry,
                                       batch=batch,
                                       config=config)

        if self.config is not None:
            self.set_loop(self.config.filter_loop)
            self.set_file_format(self.config.t1250_file_format)
            self.set_staging_base(self.config.staging_base)
            self.set_filters(self.config.filters)
            self.set_in_dirs(self.config.aggregator_dirs)
            self.set_support_emails(self.config.support_emails)

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
                        filtered_status = False
                        for dp, rules in self.filters.iteritems():
                            filtered_status = filter.process(line, rules)
                            if filtered_status:
                                kwargs = {'data': line,
                                          'fhs': fhs,
                                          'delivery_partner': dp,
                                          'infile': file,
                                          'dry': self.dry}
                                self.write(**kwargs)
                                break

                        self.reporter(filtered_status)
                f.close()
                self.close(fhs)

                if status and eof_found:
                    self.send_table(recipients=self.support_emails,
                                    table_data=list(filter.alerts),
                                    identifier=file,
                                    dry=self.dry)
                    filter.set_alerts(None)

                    stats = self.reporter.report()
                    log.info(stats)

                    if not self.dry:
                        remove_files(file)
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
            log.debug('Looking for files at: %s ...' % dir_to_check)
            for file in get_directory_files(dir_to_check):
                if (check_filename(file, self.file_format) and
                    check_eof_flag(file)):
                    log.info('Found file: "%s" ' % file)
                    files_to_process.append(file)

        files_to_process.sort()
        log.debug('Files set to be processed: "%s"' % str(files_to_process))

        return files_to_process

    def get_outbound_file(self, delivery_partner, file, dir=None):
        """Generates the path to the outbound file resource for output
        of *file* processing.

        Generation of the outbound file is based on:

        * :attr:`nparcel.b2cconfig.staging_base` attribute (or current
          directory if not identified)

        * *delivery_partner* and ``out``

        * *file* name (with ``.tmp`` appended)

        For example, if the Delivery Partner is **parcelpoint** then the
        outfile generated will be::

            ``<staging_base>/parcelpoint/out/<T1250_file>.tmp``

        **Args:**
            *file*: the name of the T1250 file currently under processing
            control

        **Kwargs:**
            *dir*: override the :attr:`nparcel.b2cconfig.staging_base`

        **Returns:**
            the path and filename to the appropriate outbound file
            resource

        """
        outfile = None

        if dir is None:
            dir = self.staging_base

        outbound_dir = os.path.join(dir, delivery_partner, 'out')

        if create_dir(outbound_dir):
            outfile = os.path.join(outbound_dir,
                                   os.path.basename(file) + '.tmp')

        log.debug('Using outfile "%s"' % outfile)
        return outfile

    def write(self, data, fhs, delivery_partner, infile, dry=False):
        """Write out *data* to the associated *fhs* file handler.

        *fhs* is based on the return value from
        :meth:`nparcel.FilterDaemon.get_outbound_file`

        **Args:**
            *data*: the line item to write out

            *fhs*: dictionary structure capturing open file handle objects

            *delivery_partner*: name of the Delivery Partner that will
            receive the filtered T1250 file

            *infile*: source T1250 EDI file that is being filtered

        """
        log.info('Writing out connote "%s" ...' % data[0:20].rstrip())

        outfile = self.get_outbound_file(delivery_partner, infile)
        fh = fhs.get(outfile)
        if fh is None:
            log.info('Preparing file handler for outfile %s' % outfile)
            if not dry:
                fhs[outfile] = open(outfile, 'w')
                fh = fhs[outfile]

        if not dry:
            fh.write('%s' % data)

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
