__all__ = [
    "PodTranslatorDaemon",
]
import signal
import time

import nparcel
from nparcel.utils.log import log


class PodTranslatorDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.PodTranslator` class.

    .. attribute:: file_formats

        list of :mod:`re` format strings to match filter files against

    """
    _config = None
    _file_formats = []

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
            self.config = nparcel.PodB2CConfig(file=config)
            self.config.parse_config()

        try:
            self.set_loop(self.config.pod_translator_loop)
        except AttributeError, err:
            log.debug('%s loop not in config: %s. Using %d (sec)' %
                      (self.facility, err, self.loop))

        try:
            if len(self.config.pod_dirs):
                self.set_in_dirs(self.config.pod_dirs)
            else:
                raise
        except AttributeError, err:
            log.debug('%s inbound dir not in config: %s. Using "%s"' %
                      (self.facility, err, self.in_dirs))

        try:
            if self.config.file_formats is not None:
                self.set_file_formats(self.config.file_format)
        except AttributeError, err:
            log.debug('%s file_formats not in config: %s. Using %s' %
                      (self.facility, err, self.file_formats))

    @property
    def file_formats(self):
        return self._file_formats

    def set_file_formats(self, values=None):
        del self._file_formats[:]
        self._file_formats = []

        if values is not None:
            self._file_formats.extend(values)
        log.debug('%s file_formats set to: "%s"' %
                  (self.facility, self.file_formats))

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

        pt = nparcel.PodTranslator()

        while not event.isSet():
            files = []
            if self.file is not None:
                files.append(self.file)
                event.set()
            else:
                files.extend(self.get_files())

            # Start processing files.
            for file in files:
                log.info('Processing file: "%s" ...' % file)

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.loop)
