__all__ = [
    "OnDeliveryDaemon",
]
import time
import signal

import top
from top.utils.log import log
from top.utils.files import (get_directory_files_list,
                             remove_files)
from top.utils.setter import (set_scalar,
                              set_tuple,
                              set_list,
                              set_dict)


class OnDeliveryDaemon(top.DaemonService):
    """Daemoniser facility for the :class:`top.OnDelivery` class.

    .. attribute:: report_in_dir

        TCD Delivery Report inbound directory
        (default ``/data/top/tcd``)

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

    .. attribute:: ts_db_kwargs

        dictionary of connection string values for the TransSend database.
        Typical format is::

            {'host': ...,
             'user': ...,
             'password': ...,
             'port': ...,
             'sid': ...}

    .. attribute od

        :mod:`top.OnDelivery` object

    .. attribute:: pe_bu_ids

        Business Unit IDs to use in the Primary Elect on delivery
        ``job_items`` table extraction

    .. attribute:: sc4_bu_ids

        Business Unit IDs to use in the Service Code 4 on delivery
        ``job_items`` table extraction

    .. attribute:: sc4_delay_bu_ids

        Business Unit IDs that use the delay template for Service Code 4
        on delivery comms

    .. attribute:: day_range

        Limit uncollected parcel search to within nominated day range
        (default 14.0 days)

    .. attribute:: file_cache_size

        number of date-orderd TCD files to load during a processing loop
        (default 5)

    .. attribute:: business_units

         dictionary of business units names and their bu_ids as per the
         business_units.id table column

    .. attribute:: comms_delivery_partners

        dictionary of Business Unit based list of Delivery Partners that
        will have comms event files created during the load process

    """
    _report_in_dirs = []
    _report_file_format = 'TCD_Deliveries_\d{14}\.DAT'
    _comms_dir = None
    _db_kwargs = None
    _ts_db_kwargs = None
    _od = None
    _pe_bu_ids = ()
    _sc4_bu_ids = ()
    _sc4_delay_bu_ids = ()
    _day_range = 14
    _file_cache_size = 5
    _business_units = {}
    _comms_delivery_partners = {}

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

    @property
    def ts_db_kwargs(self):
        return self._ts_db_kwargs

    @set_dict
    def set_ts_db_kwargs(self, value):
        pass

    @property
    def business_units(self):
        return self._business_units

    @set_dict
    def set_business_units(self, values=None):
        pass

    @property
    def comms_delivery_partners(self):
        return self._comms_delivery_partners

    @set_dict
    def set_comms_delivery_partners(self, values=None):
        pass

    @property
    def od(self):
        return self._od

    @property
    def pe_bu_ids(self):
        return self._pe_bu_ids

    @set_tuple
    def set_pe_bu_ids(self, values=None):
        pass

    @property
    def sc4_bu_ids(self):
        return self._sc4_bu_ids

    @set_tuple
    def set_sc4_bu_ids(self, values=None):
        pass

    @property
    def sc4_delay_bu_ids(self):
        return self._sc4_delay_bu_ids

    @set_tuple
    def set_sc4_delay_bu_ids(self, values=None):
        pass

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

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config=None):
        top.DaemonService.__init__(self,
                                   pidfile=pidfile,
                                   file=file,
                                   dry=dry,
                                   batch=batch,
                                   config=config)

        if self.config is not None:
            self.set_comms_dir(self.config.comms_dir)
            self.set_loop(self.config.ondelivery_loop)
            self.set_report_in_dirs(self.config.inbound_tcd)
            self.set_report_file_format(self.config.tcd_filename_format)
            self.set_db_kwargs(self.config.db_kwargs())
            self.set_ts_db_kwargs(self.config.ts_db_kwargs())
            self.set_pe_bu_ids(self.config.pe_comms_ids)
            self.set_sc4_bu_ids(self.config.sc4_comms_ids)
            self.set_sc4_delay_bu_ids(self.config.sc4_delay_ids)
            self.set_day_range(self.config.uncollected_day_range)
            self.set_file_cache_size(self.config.file_cache_size)
            self.set_business_units(self.config.business_units)
            dps = self.config.comms_delivery_partners
            self.set_comms_delivery_partners(dps)

    def set_on_delivery(self, db=None, ts_db_kwargs=None, comms_dir=None):
        """Create a OnDelivery object,

        **Kwargs:**
            *db*: :mod:`top.DbSession` object

            *ts_db_kwargs*: dictionary of key/value pairs representing
            the TransSend connection

            *comms_dir*: directory where to place comms events file
            for further processing

        """
        log.debug('Setting the OnDelivery object ...')
        if db is None:
            db = self.db_kwargs

        if ts_db_kwargs is None:
            ts_db_kwargs = self.ts_db_kwargs

        if comms_dir is None:
            comms_dir = self.comms_dir

        if self._od is None:
            self._od = top.OnDelivery(db_kwargs=db,
                                      ts_db_kwargs=ts_db_kwargs,
                                      comms_dir=comms_dir)

            if self.config is not None:
                self._od.set_delivered_header(self.config.delivered_header)
                event_key = self.config.delivered_event_key
                self._od.set_delivered_event_key(event_key)
                self._od.set_scan_desc_header(self.config.scan_desc_header)
                self._od.set_scan_desc_keys(self.config.scan_desc_keys)

    def _start(self, event):
        """Override the :method:`top.utils.Daemon._start` method.

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
            for bu_id in self.pe_bu_ids:
                log.debug('PE check for bu_id: %d' % bu_id)
                dps = self.delivery_partner_lookup(bu_id)
                kwargs = {'template': 'pe',
                          'service_code': 3,
                          'bu_ids': (bu_id, ),
                          'in_files': tcd_files,
                          'day_range': self.day_range,
                          'delivery_partners': dps,
                          'dry': self.dry}
                processed_ids = self.od.process(**kwargs)
                log.debug('PE (BU: %d) job_items.id comms created: "%s"' %
                          (bu_id, processed_ids))

            log.debug('Attempting Service Code 4 On Delivery check ...')
            for bu_id in self.sc4_bu_ids:
                log.debug('SC4 check for bu_id: %d' % bu_id)
                dps = self.delivery_partner_lookup(bu_id)
                template = self.template_lookup(bu_id)
                kwargs = {'template': template,
                          'service_code': 4,
                          'bu_ids': (bu_id, ),
                          'in_files': tcd_files,
                          'day_range': self.day_range,
                          'delivery_partners': dps,
                          'dry': self.dry}
                processed_ids = self.od.process(**kwargs)
                log.debug('SC4 (BU: %d) job_items.id comms created: "%s"' %
                          (bu_id, processed_ids))

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
        """Searches the :attr:`top.OnDeliveryDaemon.report_in_dirs`
        configuration item as the source directory for TCD report files.

        There may be more than one TCD file available for processing
        but only the most recent
        :attr:`top.OnDeliveryDaemon.file_cache_size` will be returned.
        All other files will be deleted from the system.

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            list if TCD delivery reports.  At this time, list will contain
            at most :attr:`top.OnDeliveryDaemon.file_cache_size` TCD
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

    def delivery_partner_lookup(self, bu_id):
        """Lookup method that identifies the business unit name associated
        with *bu_id* and returns a tuple of Delivery Partners to filter
        uncollected parcels against.

        **Args:**
            *bu_id*: the Business Unit ID that typically relates to the
             business_unit.id table column

        **Returns**:
            tuple of Delivery Partners that are enabled to have comms event
            files triggered

        """
        dps = ()

        bu = None
        for k, v in self.business_units.iteritems():
            if v == bu_id:
                bu = k
                break

        if bu is not None:
            tmp_dps = self.comms_delivery_partners.get(bu)
            if tmp_dps is not None:
                dps = tuple(tmp_dps)
        else:
            log.warn('BU name for ID %d was not identified' % bu_id)

        log.debug('BU ID: %d Delivery Partner lookup produced: %s' %
                  (bu_id, str(dps)))

        return dps

    def template_lookup(self, bu_id):
        """Lookup method that checks if *bu_id* has its SC4 delay template
        flag set.

        **Args:**
            *bu_id*: the Business Unit ID that typically relates to the
             business_unit.id table column

        **Returns**:
            string 'delay' if *bu_id* has its delay template flag set

            string 'body' otherwise

        """
        template = 'body'

        if bu_id in self.sc4_delay_bu_ids:
            template = 'delay'

        log.debug('BU ID|delay_flags: %d|%s using template: %s' %
                  (bu_id, str(self.sc4_delay_bu_ids), template))
        return template
