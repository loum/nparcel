__all__ = [
    "AdpDaemon",
]
import signal
import os
import time

import top
from top.utils.log import log
from top.utils.files import (get_directory_files_list,
                             move_file,
                             xlsx_to_csv_converter)
from top.utils.setter import (set_scalar,
                              set_list)


class AdpDaemon(top.DaemonService):
    """Daemoniser facility for the :class:`top.AdpParser` class.

    .. attribute:: parser

        :mod:`top.AdpParser` parser object

    .. attribute:: adp_in_dirs

        ADP bulk load inbound directory
        (default ``/var/ftp/pub/top/adp/in``)

    .. attribute:: adp_file_formats

        regular expression format string for inbound ADP bulk filenames
        (default [] in which case all files are accepted)

    .. attribute:: archive_dir

        where to archive ADP file after processing

    .. attribute:: code_header

        special ADP bulk insert header name that relates to the
        ``agent.code`` column.  This value is used as a unique
        identifier during the agent insert process

    """
    _parser = top.AdpParser()
    _adp_in_dirs = None
    _adp_file_formats = []
    _archive_dir = None
    _code_header = 'TP Code'

    @property
    def parser(self):
        return self._parser

    @property
    def adp_in_dirs(self):
        return self._adp_in_dirs

    @set_list
    def set_adp_in_dirs(self, values=None):
        pass

    @property
    def adp_file_formats(self):
        return self._adp_file_formats

    @set_list
    def set_adp_file_formats(self, values=None):
        pass

    @property
    def archive_dir(self):
        return self._archive_dir

    @set_scalar
    def set_archive_dir(self, value):
        pass

    @property
    def code_header(self):
        return self._code_header

    @set_scalar
    def set_code_header(self, value):
        pass

    @property
    def adp_kwargs(self):
        kwargs = {}
        try:
            kwargs['db'] = self.config.db_kwargs()
        except AttributeError, err:
            log.debug('DB kwargs not in config: %s ' % err)

        try:
            kwargs['headers'] = self.config.adp_headers
        except AttributeError, err:
            log.debug('ADP headers not in config: %s ' % err)

        try:
            kwargs['delivery_partners'] = self.config.delivery_partners
        except AttributeError, err:
            log.debug('ADP delivery partners not in config: %s ' % err)

        try:
            kwargs['default_passwords'] = self.config.adp_default_passwords
        except AttributeError, err:
            log.debug('ADP default passwords not in config: %s ' % err)

        return kwargs

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
            self.set_loop(self.config.adp_loop)
            self.set_adp_in_dirs(self.config.adp_dirs)
            self.set_archive_dir(self.config.archive_dir)
            self.set_adp_file_formats(self.config.adp_file_formats)
            self.set_code_header(self.config.code_header)

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

        adp = top.Adp(**(self.adp_kwargs))

        commit = True
        if self.dry:
            commit = False

        while not event.isSet():
            files = []
            if adp.db():
                if self.file is not None:
                    converted_file = xlsx_to_csv_converter(self.file)
                    if converted_file is not None:
                        files.append(converted_file)
                    event.set()
                else:
                    files.extend(self.get_files())
            else:
                log.error('ODBC connection failure -- aborting')
                event.set()
                continue

            # Start processing.
            if len(files):
                self.reporter.reset(identifier=str(files))
                self.parser.set_in_files(files)
                if self.code_header is not None:
                    self.parser.set_code_header(self.code_header)
                self.parser.read()

            for code, v in self.parser.adps.iteritems():
                self.reporter(adp.process(code, v, dry=self.dry))

            alerts = []
            if len(files):
                files_str = ', '.join(files)
                self.send_table(recipients=self.support_emails,
                                table_data=list(adp.alerts),
                                identifier=files_str,
                                dry=self.dry)
                adp.reset(commit=commit)

                # Archive the files.
                for f in files:
                    self.archive_file(f, dry=self.dry)

                stats = self.reporter.report()
                log.info(stats)

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.loop)

    def get_files(self):
        """Searches the :attr:`adp_in_dirs` directories for TCD report
        files.

        **Returns:**
            list of ADP bulk load files

        """
        files = []

        for dir in self.adp_in_dirs:
            log.debug('Searching "%s" for ADP bulk insert files' % dir)
            if len(self.adp_file_formats):
                for format in self.adp_file_formats:
                    files.extend(get_directory_files_list(dir, format))
            else:
                files.extend(get_directory_files_list(dir))

        # Convert xlsx file to csv.
        converted_files = []
        for f in files:
            tmp_file = xlsx_to_csv_converter(f)
            if tmp_file is not None:
                converted_files.append(tmp_file)

        log.debug('All ADP bulk load files: "%s"' % converted_files)

        return converted_files

    def archive_file(self, file, dry=False):
        """Will attempt to move *file* to the ADP archive directory.

        .. note::

            All attempts will be made to archive the original ``*.xlsx``
            and ``*.csv`` variant.

        **Args:**
            *file*: string representation of the filename to archive

        """
        filename = os.path.splitext(file)[0]
        file_base = os.path.basename(filename)
        log.info('Archiving "%s.*"' % filename)

        if self.archive_dir is not None:
            archive_path = os.path.join(self.archive_dir, 'adp')
            if not dry:
                for ext in ['xlsx', 'csv']:
                    move_file("%s.%s" % (filename, ext),
                              os.path.join(archive_path, "%s.%s" %
                                                         (file_base, ext)))
        else:
            log.info('Archive directory not defined -- archiving disabled')
