__all__ = [
    "AdpDaemon",
]
import signal
import os
import time

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import (get_directory_files_list,
                                 move_file,
                                 xlsx_to_csv_converter)


class AdpDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.AdpParser` class.

    .. attribute:: parser

        :mod:`nparcel.AdpParser` parser object

    .. attribute:: adp_in_dirs

        ADP bulk load inbound directory
        (default ``/var/ftp/pub/nparcel/adp/in``)

    .. attribute:: adp_file_formats

        regular expression format string for inbound ADP bulk filenames
        (default [] in which case all files are accepted)

    .. attribute:: archive_dir

        where to archive ADP file after processing

    """
    _parser = nparcel.AdpParser()
    _adp_in_dirs = [os.path.join(os.sep,
                                 'var',
                                 'ftp',
                                 'pub',
                                 'nparcel',
                                 'adp',
                                 'in')]
    _adp_file_formats = []
    _archive_dir = None

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
                                       batch=batch)

        if config is not None:
            self.config = nparcel.B2CConfig(file=config)
            self.config.parse_config()

        try:
            if self.config.support_emails is not None:
                self.set_support_emails(self.config.support_emails)
        except AttributeError, err:
            msg = ('Support emails not defined in config -- using %s' %
                   str(self.support_emails))

        try:
            self.set_adp_in_dirs(self.config.adp_dirs)
        except AttributeError, err:
            msg = ('ADP inbound dir not in config -- using %s' %
                   self.adp_in_dirs)
            log.debug(msg)

        try:
            self.set_archive_dir(self.config.archive_dir)
        except AttributeError, err:
            msg = ('Archive directory not in config -- archiving disabled')
            log.debug(msg)

        try:
            self.set_loop(self.config.adp_loop)
        except AttributeError, err:
            log.debug('Daemon loop not in config -- default %d sec' %
                      self.loop)

        try:
            self.set_adp_file_formats(self.config.adp_file_formats)
        except AttributeError, err:
            log.debug('ADP file formats not in config -- default %s' %
                      self.adp_file_formats)

    @property
    def parser(self):
        return self._parser

    @property
    def adp_in_dirs(self):
        return self._adp_in_dirs

    def set_adp_in_dirs(self, values):
        del self._adp_in_dirs[:]
        self._adp_in_dirs = []

        if values is not None:
            log.debug('Setting ADP inbound directory to "%s"' % values)
            self._adp_in_dirs.extend(values)

    @property
    def adp_file_formats(self):
        return self._adp_file_formats

    def set_adp_file_formats(self, values):
        del self._adp_file_formats[:]
        self._adp_file_formats = []

        if values is not None:
            log.debug('Setting ADP file formats to "%s"' % values)
            self._adp_file_formats.extend(values)

    @property
    def archive_dir(self):
        return self._archive_dir

    def set_archive_dir(self, value):
        self._archive_dir = value
        log.debug('Set archive directory to "%s"' % value)

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

        code_header = None
        try:
            code_header = self.config.code_header
        except AttributeError, err:
            log.debug('ADP code_header not in config: %s ' % err)

        adp = nparcel.Adp(**kwargs)

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
                if code_header is not None:
                    self.parser.set_code_header(code_header)
                self.parser.read()

            for code, v in self.parser.adps.iteritems():
                self.reporter(adp.process(code, v, dry=self.dry))

            alerts = []
            if len(files):
                alerts = list(adp.alerts)
                adp.reset(commit=commit)
                stats = self.reporter.report()
                log.info(stats)
                for f in files:
                    self.archive_file(f, dry=self.dry)

            # Report the results.
            if len(alerts):
                alert_table = self.create_table(alerts)
                del alerts[:]
                data = {'facility': self.__class__.__name__,
                        'err_table': alert_table}
                self.emailer.send_comms(template='general_err',
                                        data=data,
                                        recipients=self.support_emails,
                                        dry=self.dry)

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
