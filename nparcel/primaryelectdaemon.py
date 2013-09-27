__all__ = [
    "PrimaryElectDaemon",
]
import time
import signal

import nparcel
from nparcel.utils.log import log


class PrimaryElectDaemon(nparcel.utils.Daemon):
    """PrimaryElectDaemon class.

    """

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 config='nparcel.conf'):
        super(PrimaryElectDaemon, self).__init__(pidfile=pidfile)

        self.file = file
        self.dry = dry

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

        self.parser = nparcel.StopParser()

    def _start(self, event):
        signal.signal(signal.SIGTERM, self._exit_handler)

        pe = nparcel.PrimaryElect(db=self.config.db_kwargs(),
                                  proxy=self.config.proxy_string(),
                                  scheme=self.config.proxy_scheme,
                                  sms_api=self.config.sms_api_kwargs,
                                  email_api=self.config.email_api_kwargs)

        while not event.isSet():
            files = []

            if pe.db():
                if self.file is not None:
                    # Only makes sense to do one iteration if a single
                    # file has been given on the command line.
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
                # Only makes sense to do one iteration of a dry run.
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config.loader_loop)

    def _exit_handler(self, signal, frame):
        log_msg = '%s --' % type(self).__name__
        log.info('%s SIGTERM intercepted' % log_msg)
        self.set_exit_event()
