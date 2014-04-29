__all__ = [
    "MapperDaemon",
]
import signal
import time
import re
import os
import datetime

import top
from top.utils.log import log
from top.utils.files import (get_directory_files,
                             check_eof_flag,
                             check_filename,
                             move_file)
from top.utils.setter import set_scalar


class MapperDaemon(top.DaemonService):
    """Daemoniser facility for the :class:`top.Mapper` class.
    .. attribute:: customer

        context name of the current process iteration

    .. attribute:: file_format

        the :mod:`re` format string to match filter files against
        (default ``T1250_TOL[PIF]_\d{14}\.dat``)

    .. attribute:: file_ts_format

        Date/time string format to use to build into the T1250 outbound file
        (default ``%Y%m%d%H%M%S``)

    .. attribute:: processing_ts

        Current timestamp

    .. attribute:: archive_string

        regular expression grouping that represent the YYYYMMDD date
        sequence of inbound filenames (default
        T1250_TOL[PIF]_(\d{8})\d{6}\.dat)

    """
    _config = None
    _customer = 'gis'
    _file_format = 'T1250_TOL[PIF]_\d{14}\.dat'
    _file_ts_format = '%Y%m%d%H%M%S'
    _processing_ts = datetime.datetime.now()
    _archive_string = 'T1250_TOL[PIF]_(\d{8})\d{6}\.dat'

    @property
    def file_format(self):
        return self._file_format

    @set_scalar
    def set_file_format(self, value):
        pass

    @property
    def file_ts_format(self):
        return self._file_ts_format

    def set_file_ts_format(self, value):
        self._file_ts_format = value

    @property
    def processing_ts(self):
        return self._processing_ts

    def set_processing_ts(self, value=None):
        if value is None:
            self._processing_ts = datetime.datetime.now()
        else:
            self._processing_ts = value

    @property
    def customer(self):
        return self._customer

    @set_scalar
    def set_customer(self, value):
        pass

    @property
    def archive_string(self):
        return self._archive_string

    @set_scalar
    def set_archive_string(self, value):
        pass

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config=None):
        top.DaemonService.__init__(self,
                                   pidfile=pidfile,
                                   file=file,
                                   dry=dry,
                                   batch=batch,
                                   config=config)

        if self.config is not None:
            self.set_archive_base(self.config.archive_dir)
            self.set_loop(self.config.mapper_loop)
            self.set_customer(self.config.pe_customer)
            self.set_in_dirs(self.config.mapper_in_dirs)
            self.set_file_format(self.config.pe_in_file_format)
            self.set_archive_string(self.config.pe_in_file_archive_string)

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

        mapper = top.Mapper()
        reporter = top.Reporter()

        while not event.isSet():
            fhs = {}
            files = []
            if self.file is not None:
                files.append(self.file)
                event.set()
            else:
                files.extend(self.get_files())

            # Start processing files.
            batch_ok = True
            for file in files:
                log.info('Processing file: "%s" ...' % file)
                status = False
                dir = os.path.dirname(file)
                self.set_processing_ts()

                try:
                    f = open(file, 'r')
                except IOError, e:
                    log.error('File open error "%s": %s' % (file, str(e)))
                    continue

                reporter.reset(identifier=file)
                eof_found = False
                for line in f:
                    record = line.rstrip('\r\n')
                    if record == '%%EOF':
                        log.info('EOF found')
                        status = True
                        eof_found = True
                        break
                    else:
                        translated_line = mapper.process(line)
                        reporter(translated_line)
                        if translated_line:
                            self.write(translated_line,
                                       fhs,
                                       dir,
                                       dry=self.dry)

                f.close()

                if status:
                    log.info('%s processing OK.' % file)
                    stats = reporter.report()
                    log.info(stats)
                else:
                    batch_ok = False
                    log.error('%s processing failed.' % file)
                    if not eof_found:
                        log.error("%s - %s" % ('File closed before EOF',
                                               'all line items ignored'))

            if batch_ok:
                closed_files = self.close(fhs)
                log.debug('Inbound T1250 files produced: "%s"' %
                          str(closed_files))

                # Archive files.
                for file in files:
                    archive_path = self.get_customer_archive(file)
                    if not self.dry:
                        move_file(file, archive_path, err=True)
            else:
                # Just close the files as they are.
                for fh in fhs.values():
                    fh.close()

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
        """Identifies GIS-special WebMethod files that are to be processed.

        Check performed are:

        * T1250 has a trailing ``%%EOF\\r\\n`` token (completed transfer)

        * Filename conforms to the WebMethods format
        * File is not in the archive (already been processed)

        **Args:**
            *dir*: directory to search

        **Returns:**
            date sorted list of WebMethods files to process

        """
        files_to_process = []

        dirs_to_check = self.in_dirs
        if dir is not None:
            dirs_to_check = dir

        for dir_to_check in dirs_to_check:
            log.debug('Looking for files at: %s ...' % dir_to_check)
            for file in get_directory_files(dir_to_check):
                if (check_filename(file, self.file_format) and
                    check_eof_flag(file)):
                    log.info('Found file: %s' % file)
                    archive_path = self.get_customer_archive(file)
                    if (archive_path is not None and
                        os.path.exists(archive_path)):
                        log.error('File %s is already archived' % file)
                    else:
                        files_to_process.append(file)

        files_to_process.sort()
        log.debug('Files set to be processed: "%s"' % str(files_to_process))

        return files_to_process

    def get_customer_archive(self, file):
        """Returns the archive target path based on GIS T1250 filename
        *file*.  For example, if the source file is
        ``<ftp_base>/top/in/T1250_TOLI_20131011115618.dat`` then the
        archive target would be similar to
        ``<archive_base>/gis/20131011/T1250_TOLI_20131011115618.dat``

        **Args:**
            file: the inbound GIS WebMethods T1250 file.

        **Returns:**
            string representation of the absolute path to the *file*'s
            archive target

        """
        filename = os.path.basename(file)
        archive_dir = None
        archive_path = None

        m = re.search(self.archive_string, filename)
        if m is not None:
            file_timestamp = m.group(1)
            dir = os.path.join(self.archive_base,
                               self.customer,
                               file_timestamp)
            archive_path = os.path.join(dir, filename)

        return archive_path

    def write(self, data, fhs, dir=None, dry=False):
        """Writes out the Business Unit-specific record string contained
        within *data* to a T1250 file.

        **Args:**
            *data*: a tuple structure in the form
            ``(<business_unit>, <translated_T1250_data>)``

            *fhs*: dictionary structure capturing open file handle objects

            *dir*: base directory to write file to

            *dry*: only report, do not execute

        **Returns:**
            boolean ``True`` if write was successful

            boolean ``False`` if write failed

        """
        status = True

        if dir is None:
            dir = os.curdir

        if not data:
            log.error('Trying to write out invalid data: "%s"' % str(data))
            status = False
        else:
            (bu, record) = data

            fh = fhs.get(bu)
            if fh is None:
                file_ts = self.processing_ts.strftime(self.file_ts_format)
                file = 'T1250_%s_%s.txt.tmp' % (bu.upper(), file_ts)
                filepath = os.path.join(dir, file)
                log.info('Creating file %s for Business Unit "%s"' %
                         (filepath, bu))
                if not dry:
                    fhs[bu] = open(filepath, 'w')
                    fh = fhs[bu]

            if not dry:
                fh.write('%s\n' % record)

        return status

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
        files_closed = []

        temp_format = 'T1250_TOL[PIF]_\d{14}\.txt\.tmp'
        r = re.compile(temp_format)
        for fh in fhs.values():
            filename = fh.name
            file = os.path.basename(filename)
            log.debug('Checking format of temp file: %s' % file)
            m = r.match(os.path.basename(file))
            if not m:
                log.info('File %s did not match format %s' %
                         (file, temp_format))
                continue

            fh.write('%%EOF\r\n')
            fh.close()

            # ... and finally convert to T1250-proper.
            source = filename
            target = re.sub('\.tmp$', '', source)
            if move_file(source, target):
                files_closed.append(target)

        return files_closed
