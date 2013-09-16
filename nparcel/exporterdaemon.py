__all__ = [
    "ExporterDaemon",
]
import os
import time
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

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

    def _start(self, event):
        signal.signal(signal.SIGTERM, self._exit_handler)

        sig_dir = self.config('signature_dir')
        staging_dir = self.config('staging_base')
        archive_dir = self.config('archive_dir')
        if archive_dir is not None:
            archive_dir = os.path.join(archive_dir, 'signature')
        exporter = nparcel.Exporter(db=self.config.db_kwargs(),
                                    signature_dir=sig_dir,
                                    staging_dir=staging_dir,
                                    archive_dir=archive_dir)

        while not event.isSet():
            if exporter.db():
                for bu, id in self.config('business_units').iteritems():
                    log.info('Starting collection report for BU "%s" ...' %
                             bu)
                    exporter.set_out_dir(business_unit=bu)
                    bu_file_code = self.config.bu_to_file(bu)
                    file_control = self.config.get_file_control(bu_file_code)
                    items = exporter.process(int(id),
                                             file_control,
                                             dry=self.dry)
                    if self.dry:
                        exporter.set_out_dir(None)
                    seq = self.config('exporter_fields').get(bu_file_code)
                    identifier = bu[0].upper()
                    state_rep = self.config.condition(bu_file_code,
                                                      'state_reporting')
                    exporter.report(items,
                                    sequence=seq,
                                    identifier=identifier,
                                    state_reporting=state_rep)
                    exporter.reset()
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
