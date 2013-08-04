__all__ = [
    "ExporterDaemon",
]
import signal

import nparcel
from nparcel.utils.log import log


class ExporterDaemon(nparcel.utils.Daemon):

    def __init__(self,
                 pidfile,
                 config='nparcel.conf'):
        super(ExporterDaemon, self).__init__(pidfile=pidfile)

        self.config = nparcel.Config(file=config)

    def _start(self, event):
        signal.signal(signal.SIGTERM, self._exit_handler)

        exporter = nparcel.Exporter(db=self.config.db_kwargs())

        while not event.isSet():
            event.set()

    def _exit_handler(self, signal, frame):
        log_msg = '%s --' % type(self).__name__
        log.info('%s SIGTERM intercepted' % log_msg)
        self.set_exit_event()
