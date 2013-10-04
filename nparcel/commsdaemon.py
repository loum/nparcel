__all__ = [
    "CommsDaemon",
]
import signal
import time

import nparcel
from nparcel.utils.log import log


class CommsDaemon(nparcel.utils.Daemon):
    """CommsDaemon class.
    """

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 config='nparcel.conf'):
        super(CommsDaemon, self).__init__(pidfile=pidfile)

        self.file = file
        self.dry = dry

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

    def _start(self, event):
        """Override the :method:`nparcel.utils.Daemon._start` method.

        Will perform a single iteration if the :attr:`file` attribute has
        a list of filenames to process.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        comms = nparcel.Comms(db=self.config.db_kwargs(),
                              comms_dir=self.config.comms_dir)

        while not event.isSet():
            files = []

            if comms.db():
                if self.file is not None:
                    files.append(self.file)
                    event.set()
                else:
                    files.extend(comms.get_comms_files())
            else:
                log.error('ODBC connection failure -- aborting')
                event.set()
                continue

            # Start processing files.
            for file in files:
                log.info('Processing file: "%s" ...' % file)
                comms.process(file, self.dry)

            if not event.isSet():
                # Only makes sense to do one iteration of a dry run.
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config.comms_loop)

    def _exit_handler(self, signal, frame):
        log_msg = '%s --' % type(self).__name__
        log.info('%s SIGTERM intercepted' % log_msg)
        self.set_exit_event()
