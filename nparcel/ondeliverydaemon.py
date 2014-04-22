__all__ = [
    "OnDeliveryDaemon",
]
import time
import signal

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import (get_directory_files_list,
                                 remove_files)
from nparcel.utils.setter import (set_scalar,
                                  set_tuple,
                                  set_list,
                                  set_dict)


class OnDeliveryDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.OnDelivery` class.

    .. attribute:: report_in_dir

        TCD Delivery Report inbound directory
        (default ``/data/nparcel/tcd``)

    .. attribute:: report_file_format

        regular expression format string for inbound delivery report
        filename (default ``TCD_Deliveries_\d{14}\.DAT``)

    .. attribute:: comms_dir

        directory where comms files are kept for further processing

    .. attribute:: db_kwargs

        dictionary of connection string values for the Toll Parcel Point
        database.  Typical format is::

            {'driver': ...,
             'host': ...,
             'database': ...,
             'user': ...,
             'password': ...,
             'port': ...}

    .. attribute od

        :mod:`nparcel.OnDelivery` object

    .. attribute:: pe_bu_ids

        Business Unit IDs to use in the Primary Elect on delivery
        ``job_items`` table extraction

    .. attribute:: sc4_bu_ids

        Business Unit IDs to use in the Service Code 4 on delivery
        ``job_items`` table extraction

    .. attribute:: day_range

        Limit uncollected parcel search to within nominated day range
        (default 14.0 days)

    .. attribute:: file_cache_size

        number of date-orderd TCD files to load during a processing loop
        (default 5)

    """
    _config = None
    _report_in_dirs = []
    _report_file_format = 'TCD_Deliveries_\d{14}\.DAT'
    _comms_dir = None
    _db_kwargs = None
    _od = None
    _pe_bu_ids = ()
    _sc4_bu_ids = ()
    _day_range = 14
    _file_cache_size = 5

    @property
    def report_in_dirs(self):
        return self._report_in_dirs

    @set_list
    def set_report_in_dirs(self, values=None):
        pass

    @property
    def report_file_format(self):
        return self._report_file_format

    @set_scalar
    def set_report_file_format(self, value):
        pass

    @property
    def comms_dir(self):
        return self._comms_dir

    @set_scalar
    def set_comms_dir(self, value):
        pass

    @property
    def db_kwargs(self):
        return self._db_kwargs

    @set_dict
    def set_db_kwargs(self, value):
        pass

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config=None):
        c = None
        if config is not None:
            c = nparcel.B2CConfig(config)
        nparcel.DaemonService.__init__(self,
                                       pidfile=pidfile,
                                       file=file,
                                       dry=dry,
                                       batch=batch,
                                       config=c)

        if self.config is not None:
            self.set_comms_dir(self.config.comms_dir)
            self.set_loop(self.config.ondelivery_loop)
            self.set_report_in_dirs(self.config.inbound_tcd)
            self.set_report_file_format(self.config.tcd_filename_format)
            self.set_db_kwargs(self.config.db_kwargs())
            self.set_pe_bu_ids(self.config.pe_comms_ids)
            self.set_sc4_bu_ids(self.config.sc4_comms_ids)
            self.set_day_range(self.config.uncollected_day_range)
            self.set_file_cache_size(self.config.file_cache_size)

    @property
    def od(self):
        return self._od

    @property
    def pe_bu_ids(self):
        return self._pe_bu_ids

    @set_tuple
    def set_pe_bu_ids(self, values):
        pass

    @property
    def sc4_bu_ids(self):
        return self._sc4_bu_ids

    def set_sc4_bu_ids(self, values):
        self._sc4_bu_ids = values

    @property
    def day_range(self):
        return self._day_range

    @set_scalar
    def set_day_range(self, value):
        pass

    @property
    def file_cache_size(self):
        return self._file_cache_size

    @set_scalar
    def set_file_cache_size(self, value):
        pass

    def set_on_delivery(self, db=None, ts_db_kwargs=None, comms_dir=None):
        """Create a OnDelivery object,

        **Kwargs:**
            *db*: :mod:`nparcel.DbSession` object

            *ts_db_kwargs*: dictionary of key/value pairs representing
            the TransSend connection

            *comms_dir*: directory where to place comms events file
            for further processing

        """
        log.debug('Setting the OnDelivery object ...')
        if db is None:
            db = self.db_kwargs

        if ts_db_kwargs is None:
            try:
                ts_db_kwargs = self.config.ts_db_kwargs()
            except AttributeError, err:
                log.debug('TransSend DB kwargs not defined in config')

        if comms_dir is None:
            comms_dir = self.comms_dir

        if self._od is None:
            self._od = nparcel.OnDelivery(db_kwargs=db,
                                          ts_db_kwargs=ts_db_kwargs,
                                          comms_dir=comms_dir)

            try:
                self._od.set_delivered_header(self.config.delivered_header)
            except AttributeError, err:
                log.debug('Using default delivered_header: "%s"' %
                          self._od.delivered_header)

            try:
                event_key = self.config.delivered_event_key
                self._od.set_delivered_event_key(event_key)
            except AttributeError, err:
                log.debug('Using default delivered_event_key: "%s"' %
                          self._od.delivered_event_key)

            try:
                self._od.set_scan_desc_header(self.config.scan_desc_header)
            except AttributeError, err:
                log.debug('Using default scan_desc_header: "%s"' %
                          self._od.scan_desc_header)

            try:
                self._od.set_scan_desc_keys(self.config.scan_desc_keys)
            except AttributeError, err:
                log.debug('Using default scan_desc_keys: "%s"' %
                          self._od.scan_desc_keys)

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

        self.set_on_delivery(comms_dir=self.comms_dir)

        while not event.isSet():
            tcd_files = []

            if not self.od.db() or not self.od.ts_db():
                log.error('ODBC connection failure -- aborting')
                event.set()
            else:
                if self.file is not None:
                    tcd_files.append(self.file)
                    event.set()
                else:
                    tcd_files.extend(self.get_files(dry=self.dry))

            log.debug('Attempting On Delivery Primary Elect check ...')
            if len(self.pe_bu_ids):
                kwargs = {'template': 'pe',
                          'service_code': 3,
                          'bu_ids': self.pe_bu_ids,
                          'in_files': tcd_files,
                          'day_range': self.day_range,
                          'dry': self.dry}
                processed_ids = self.od.process(**kwargs)
                log.debug('PE job_items.id comms files created: "%s"' %
                          processed_ids)
            else:
                log.debug("No Primary Elect BU ID's defined -- skipping")

            log.debug('Attempting Service Code 4 On Delivery check ...')
            if len(self.sc4_bu_ids):
                kwargs = {'template': 'body',
                          'service_code': 4,
                          'bu_ids': self.sc4_bu_ids,
                          'in_files': tcd_files,
                          'day_range': self.day_range,
                          'dry': self.dry}
                processed_ids = self.od.process(**kwargs)
                log.debug('SC 4 job_items.id comms files created: "%s"' %
                          processed_ids)
            else:
                log.debug("No Service Code 4 BU ID's defined -- skipping")

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.loop)

    def get_files(self, dry=False):
        """Searches the :attr:`nparcel.OnDeliveryDaemon.report_in_dirs`
        configuration item as the source directory for TCD report files.

        There may be more than one TCD file available for processing
        but only the most recent
        :attr:`nparcel.OnDeliveryDaemon.file_cache_size` will be returned.
        All other files will be deleted from the system.

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            list if TCD delivery reports.  At this time, list will contain
            at most :attr:`nparcel.OnDeliveryDaemon.file_cache_size` TCD
            report files (or zero) if not matches are found.

        """
        files = []
        for report_in_dir in self.report_in_dirs:
            log.debug('Searching "%s" for report files' % report_in_dir)
            files.extend(get_directory_files_list(report_in_dir,
                                                  self.report_file_format))

        files.sort()
        log.debug('All report files: "%s"' % files)

        files_to_parse = []
        if len(files):
            files_to_parse.extend(files[(-1 * self.file_cache_size):])
            log.debug('Using report files: %s' % str(files))

        for f in [x for x in files if x not in files_to_parse]:
            log.info('Purging report file: "%s"' % f)
            if not dry:
                remove_files(f)

        return files_to_parse
