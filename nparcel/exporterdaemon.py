__all__ = [
    "ExporterDaemon",
]
import os
import time
import signal

import nparcel
from nparcel.utils.log import log


class ExporterDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.Exporter` class.
    """
    _exporter = None

    def __init__(self,
                 pidfile,
                 dry=False,
                 batch=False,
                 config=None):
        nparcel.DaemonService.__init__(self,
                                       pidfile=pidfile,
                                       dry=dry,
                                       batch=batch)

        if config is not None:
            self.config = nparcel.ExporterB2CConfig(file=config)
            self.config.parse_config()

        try:
            if self.config.support_emails is not None:
                self.set_support_emails(self.config.support_emails)
        except AttributeError, err:
            msg = ('Support emails not defined in config -- using %s' %
                   str(self.support_emails))
            log.info(msg)

    @property
    def exporter(self):
        return self._exporter

    @property
    def exporter_kwargs(self):
        kwargs = {}
        try:
            kwargs['db'] = self.config.db_kwargs()
        except AttributeError, err:
            log.debug('DB kwargs not in config: %s ' % err)

        try:
            kwargs['signature_dir'] = self.config.signature_dir
        except AttributeError, err:
            log.debug('DB kwargs not in config: %s ' % err)

        try:
            kwargs['staging_dir'] = self.config.staging_base
        except AttributeError, err:
            log.debug('Staging directory not in config: %s ' % err)

        try:
            kwargs['archive_dir'] = os.path.join(self.config.archive_dir,
                                                 'signature')
        except AttributeError, err:
            log.debug('Staging directory not in config: %s ' % err)

        try:
            kwargs['exporter_dirs'] = self.config.exporter_dirs
        except AttributeError, err:
            log.debug('Exporter dirs not in config: %s ' % err)

        try:
            kwargs['exporter_file_formats'] = self.config.exporter_file_formats
        except AttributeError, err:
            log.debug('Exporter file formats not in config: %s ' % err)

        try:
            kwargs['connote_header'] = self.config.connote_header
        except AttributeError, err:
            log.debug('Connote header not in config: %s ' % err)

        try:
            kwargs['item_nbr_header'] = self.config.item_nbr_header
        except AttributeError, err:
            log.debug('Item number header not in config: %s' % err)

        return kwargs

    def _start(self, event):
        signal.signal(signal.SIGTERM, self._exit_handler)

        if self.exporter is None:
            self._exporter = nparcel.Exporter(**(self.exporter_kwargs))

        while not event.isSet():
            if self.exporter.db():
                for bu, id in self.config.business_units.iteritems():
                    log.info('Starting collection report for BU "%s" ...' %
                             bu)
                    self.exporter.set_out_dir(business_unit=bu)
                    bu_file_code = self.config.bu_to_file(bu)
                    file_ctrl = self.config.get_pod_control(bu_file_code)
                    archive_ctrl = self.config.get_pod_control(bu_file_code,
                                                               'archive')
                    ignore_pe = self.config.condition(bu, 'pe_pods')
                    items = self.exporter.process(int(id),
                                                  file_ctrl,
                                                  archive_ctrl,
                                                  ignore_pe,
                                                  dry=self.dry)
                    if self.dry:
                        self.exporter.set_out_dir(None)
                    seq = self.config.exporter_fields.get(bu_file_code)
                    identifier = bu[0].upper()
                    state_rep = self.config.condition(bu_file_code,
                                                      'state_reporting')
                    self.exporter.report(items,
                                         sequence=seq,
                                         identifier=identifier,
                                         state_reporting=state_rep)
                    self.send_table(recipients=self.support_emails,
                                    table_data=list(self.exporter.alerts),
                                    template='general_err',
                                    dry=self.dry)
                    self.exporter.reset()

                # File based closures.
                self.exporter.file_based_updates(dry=self.dry)
                self.send_table(recipients=self.support_emails,
                                table_data=list(self.exporter.alerts),
                                template='general_err',
                                dry=self.dry)
                self.exporter.reset()
            else:
                log.error('ODBC connection failure -- aborting')
                event.set()

            if not event.isSet():
                # Only makes sense to do one iteration of a dry run.
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config.exporter_loop)
