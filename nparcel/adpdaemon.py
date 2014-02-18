__all__ = [
    "AdpDaemon",
]
import signal

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import get_directory_files_list


class AdpDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.AdpParser` class.

    .. attribute:: adp_in_dirs

        ADP bulk load inbound directory
        (default ``/var/ftp/pub/nparcel/adp/in``)

    .. attribute:: adp_file_formats

        regular expression format string for inbound ADP bulk filenames
        (default [] in which case all files are accepted)

    """

    _config = None
    _adp_in_dirs = ['/var/ftp/pub/nparcel/adp/in']
    _adp_file_formats = []

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config=None):
        super(AdpDaemon, self).__init__(pidfile=pidfile,
                                        file=file,
                                        dry=dry,
                                        batch=batch)

        config_file = None
        if config is not None:
            config_file = config

        if config_file is not None:
            self.config = nparcel.B2CConfig(file=config)
            self.config.parse_config()

        try:
            self.set_adp_in_dirs(self.config.adp_dirs)
        except AttributeError, err:
            msg = ('ADP inbound dir not in config -- using %s' %
                   self.adp_in_dirs)
            log.debug(msg)

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

        while not event.isSet():
            files = []
            if self.file is not None:
                files.append(self.file)
                event.set()
            else:
                files.extend(self.get_files())

            # TODO -- Start processing.
            for file in files:
                log.info('Processing file: "%s" ...' % file)

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()

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

        log.debug('All ADP bulk load files: "%s"' % files)

        return files
