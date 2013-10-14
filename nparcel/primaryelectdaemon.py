__all__ = [
    "PrimaryElectDaemon",
]
import time
import signal

import nparcel
from nparcel.utils.log import log


class PrimaryElectDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.PrimaryElect` class.
    """

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config='nparcel.conf'):
        super(PrimaryElectDaemon, self).__init__(pidfile=pidfile,
                                                 file=file,
                                                 dry=dry,
                                                 batch=batch)

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

        self.parser = nparcel.StopParser()

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

        pe = nparcel.PrimaryElect(db=self.config.db_kwargs(),
                                  comms_dir=self.config.comms_dir)

        while not event.isSet():
            files = []

            if pe.db():
                if self.file is not None:
                    files.append(self.file)
                    event.set()
                # Only support command line file processing for now.
                #else:
                #    files.extend(self.get_files())
            else:
                log.error('ODBC connection failure -- aborting')
                event.set()
                continue

            # Start processing files.
            for file in files:
                log.info('Processing file: "%s" ...' % file)
                self.parser.set_in_file(file)
                for con in self.parser.read('Con Note'):
                    log.info('Checking connote: "%s"' % con)
                    pe.process([con], dry=self.dry)

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config.loader_loop)
