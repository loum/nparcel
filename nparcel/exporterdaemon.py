__all__ = [
    "ExporterDaemon",
]
import signal

import nparcel
from nparcel.utils.log import log


class ExporterDaemon(nparcel.utils.Daemon):

    def __init__(self,
                 pidfile,
                 dry=False,
                 config='nparcel.conf'):
        super(ExporterDaemon, self).__init__(pidfile=pidfile)

        self.dry = dry

        self.config = nparcel.Config(file=config)

    def _start(self, event):
        signal.signal(signal.SIGTERM, self._exit_handler)

        exporter = nparcel.Exporter(db=self.config.db_kwargs())

        commit = True
        if self.dry:
            commit = False

        while not event.isSet():
            if exporter.db():
                for bu, id in self.config('business_units').iteritems():
                    log.info('Starting collection report for BU "%s" ...' %
                             bu)
                    exporter.get_collected_items(business_unit=int(id),
                                                dry=self.dry)
                    exporter.report(dry=self.dry)
                    exporter.reset()

                # Only makes sense to do one iteration of a dry run.
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config('exporter_loop'))
            else:
                log.error('ODBC connection failure -- aborting')
                event.set()

            if not event.isSet():
                # Only makes sense to do one iteration of a dry run.
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config('exporter_loop'))

    def _exit_handler(self, signal, frame):
        log_msg = '%s --' % type(self).__name__
        log.info('%s SIGTERM intercepted' % log_msg)
        self.set_exit_event()
