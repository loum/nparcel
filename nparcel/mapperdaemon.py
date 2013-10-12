__all__ = [
    "MapperDaemon",
]
import signal
import time

import nparcel
from nparcel.utils.log import log


class MapperDaemon(nparcel.utils.Daemon):
    """Daemoniser facility for the :class:`nparcel.Loader` class.

    """
    _file_to_process = None
    _dry = False
    _batch = False

    def __init__(self,
                 pidfile,
                 file_to_process=None,
                 dry=False,
                 batch=False,
                 config='nparcel.conf'):
        super(MapperDaemon, self).__init__(pidfile=pidfile)

        self._file = file
        self._dry = dry
        self._batch = batch

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

    @property
    def file_to_process(self):
        return self._file_to_process

    @property
    def dry(self):
        return self._dry

    def set_dry(self, value=True):
        self._dry = value

    @property
    def batch(self):
        return self._batch

    def set_batch(self, value):
        self._batch = value

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
                else:
                    time.sleep(self.config.loader_loop)