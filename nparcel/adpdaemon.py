__all__ = [
    "AdpDaemon",
]
import signal

import nparcel
from nparcel.utils.log import log


class AdpDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.AdpParser` class.
    """
    _config = None

    def __init__(self,
                 pidfile,
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
            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
