__all__ = [
    "B2CConfig",
]
import sys
import time
import datetime

import nparcel
import ConfigParser
from nparcel.utils.log import log

FLAG_MAP = {'item_number_excp': 0,
            'send_email': 1,
            'send_sms': 2,
            'send_ps_file': 3,
            'send_png_file': 4,
            'state_reporting': 5,
            'pe_pods': 6,
            'aggregate_files': 7,
            'send_sc_1': 8,
            'send_sc_2': 9,
            'send_sc_4': 10,
            'delay_template_sc_4': 11,
            'ignore_sc_4': 12,
            'pe_comms': 13,
            'on_del_sc_4': 14,
            'archive_ps_file': 15,
            'archive_png_file': 16,
            'delay_template_sc_2': 17}


class B2CConfig(nparcel.Config):
    """B2CConfig class.

    :class:`nparcel.B2CConfig` captures the configuration items required
    by the Nparcel B2C Replicator

    .. attribute:: prod

        hostname of the production instance

    .. attribute:: dirs_to_check (loader)

        list of directories to look for T1250 files

    .. attribute:: archive_dir

        base directory where working files are archived to

    .. attribute:: staging_base (exporter)

        directory to place processed collected reports and signature files
        for further processing.

    .. attribute:: comms (loader, primary elect)

        directory where comms files are kept for further processing

    .. attribute:: aggregators (ParcelPoint processing)

        directory where T1250 loader files are aggregated for further
        processing

    .. attribute:: adp_dirs (ADP bulk load processing)

        directory list for ADP bulk load files (into ``agent`` table)

    .. attribute loader_loop (loader)

        time (seconds) between loader processing iterations.

    .. attribute onleilvery_loop (on delivery)

        time (seconds) between on delivery processing iterations.

    .. attribute reminder_loop (reminder)

        time (seconds) between primary elect processing iterations.

    .. attribute:: exporter_loop (exporter)

        time (seconds) between exporter processing iterations.

    .. attribute:: mapper_loop (mapper)

        time (seconds) between mapper processing iterations.

    .. attribute:: filter_loop (filter)

        time (seconds) between filter processing iterations.

    .. attribute:: adp_loop (ADP bulk load)

        time (seconds) between filter processing iterations.

    .. attribute:: business_units (exporter)

        the list of business units to query for collected items

    .. attribute:: t1250_file_format

        T1250 filename format

    .. attribute:: cond (loader)

        dictionary of Business unit special condition flags

    .. attribute:: email

        list of email addresses to be advised of support related processing
        issues

    .. attribute:: rest (loader)

        dictionary of RESTful interfaces for SMS and email

    .. attribute:: notification_period (reminder)

        period (in seconds) that triggers a reminder notice

    .. attribute:: start_date (reminder)

        ignores records whose job_item.created_ts occurs before this date

    .. attribute:: hold_period (reminder)

        defines the time period (in seconds) since the job_item.created_ts
        that the agent will hold the parcel before being returned

    .. attribute:: exporter_fields (exporter)

        dictionary of business unit exporter ordered columns

    .. attribute:: pe_in_file_format

        filename structure to parse for Primary Elect inbound
        (default 'T1250_TOL[PIF]_\d{14}\.dat')

    .. attribute:: pe_in_file_archive_string

        regular expression grouping structure for Primary Elect inbound
        filenames that represent the YYYYMMDD date sequence (default
        T1250_TOL[PIF]_(\d{8})\d{6}\.dat

    .. attribute:: pe_customer

        upstream provider of the T1250 files (default "gis")

    .. attribute:: inbound_tcd

        TCD Delivery Report inbound directory
        (default ``/var/ftp/pub/nparcel/tcd/in``)

    .. attribute:: tcd_filename_format

        regular expression format string for TCD delivery
        reports inbound filenames
        (default ``TCD_Deliveries_\d{14}\.DAT``)

    .. attribute:: uncollected_day_range

        limit uncollected parcel search to within nominated day range
        (default 14.0 days)

    .. attribute:: file_cache_size

        number of date-orderd TCD files to load during a processing loop
        (default 5)

    .. attribute:: filter_customer

        downstream recipient of filtered T1250 files
        (default ``parcelpoint``)

    .. attribute:: filtering_rules

        list of tokens to match against the start of the agent code field

    .. attribute:: delivered_header

        string that represents the TransSend column header name for
        a delivered item (default ``latest_scan_event_action``)

    .. attribute:: delivered_event_key

        string that represents a delivered event
        (default ``delivered``)

    .. attribute:: scan_desc_header

        the scanned description column header in TransSend
        (default ``latest_scanner_description``)

    .. attribute:: scan_desc_keys

        list of :attr:`scan_desc_header` tokens to compare against
        (default ``IDS - TOLL FAST GRAYS ONLINE``)

    .. attribute:: health_processes

        the names of the processes to include in the health check

    .. attribute:: adp_headers

        dictionary of ``agent`` table columns to column headers in the
        ADP bulk insert file

    .. attribute:: adp_file_formats

        list of regular expressions that represent the type of files that
        can be parsed by the ADP loader

    .. attribute:: code_header

        special ADP bulk insert header name that relates to the
        ``agent.code`` column.  This value is used as a unique
        identifier during the agent insert process

    .. attribute:: delivery_partners

        list of "delivery_partner" table values

    .. attribute:: adp_default_passwords

        dictionary of delivery partner default passwords

    """
    _prod = None
    _dirs_to_check = []
    _mapper_in_dirs = []
    _archive = None
    _staging_base = None
    _comms = None
    _aggregator_dirs = []
    _adp_dirs = []
    _loader_loop = 30
    _ondelivery_loop = 30
    _reminder_loop = 3600
    _exporter_loop = 300
    _mapper_loop = 30
    _filter_loop = 30
    _adp_loop = 30
    _proxy_scheme = 'https'
    _business_units = {}
    _t1250_file_format = 'T1250_TOL.*\.txt'
    _file_bu = {}
    _cond = {}
    _support_emails = []
    _rest = {}
    _notification_delay = 345600
    _start_date = datetime.datetime(2013, 9, 10, 0, 0, 0)
    _hold_period = 691200
    _exporter_fields = {}
    _pe_in_file_format = 'T1250_TOL[PIF]_\d{14}\.dat'
    _pe_in_file_archive_string = 'T1250_TOL[PIF]_(\d{8})\d{6}\.dat'
    _pe_customer = 'gis'
    _inbound_tcd = ['/var/ftp/pub/nparcel/tcd/in']
    _tcd_filename_format = 'TCD_Deliveries_\d{14}\.DAT'
    _uncollected_day_range = 14.0
    _file_cache_size = 5
    _filter_customer = 'parcelpoint'
    _filtering_rules = ['P', 'R']
    _delivered_header = 'latest_scan_event_action'
    _delivered_event_key = 'delivered'
    _scan_desc_header = 'latest_scanner_description'
    _scan_desc_keys = ['IDS - TOLL FAST GRAYS ONLINE']
    _health_processes = []
    _adp_headers = {}
    _adp_file_formats = []
    _code_header = None
    _delivery_partners = []
    _adp_default_passwords = {}

    def __init__(self, file=None):
        """B2CConfig initialisation.
        """
        nparcel.Config.__init__(self, file)

    @property
    def prod(self):
        return self._prod

    def set_prod(self, value=None):
        self._prod = value
        log.debug('%s environment.prod set to "%s"' %
                  (self.facility, self.prod))

    @property
    def in_dirs(self):
        return self._dirs_to_check

    def set_in_dirs(self, values):
        del self._dirs_to_check[:]
        self._dirs_to_check = []

        if values is not None:
            log.debug('Set inbound directory "%s"' % str(values))
            self._dirs_to_check.extend(values)

    @property
    def archive_dir(self):
        return self._archive

    def set_archive_dir(self, value):
        self._archive = value
        log.debug('%s dirs.archive set to "%s"' %
                  (self.facility, self.archive_dir))

    @property
    def staging_base(self):
        return self._staging_base

    def set_staging_base(self, value):
        self._staging_base = value
        log.debug('%s dirs.staging_base set to "%s"' %
                  (self.facility, self.staging_base))

    @property
    def comms_dir(self):
        return self._comms

    def set_comms_dir(self, value):
        log.info('Set config comms directory to "%s"' % value)
        self._comms = value

    @property
    def aggregator_dirs(self):
        return self._aggregator_dirs

    def set_aggregator_dirs(self, values):
        del self._aggregator_dirs[:]
        self._aggregator_dirs = []

        if values is not None:
            log.debug('Set config aggregator in directories "%s"' %
                      str(values))
            self._aggregator_dirs.extend(values)

    @property
    def adp_dirs(self):
        return self._adp_dirs

    def set_adp_dirs(self, values):
        del self._adp_dirs[:]
        self._adp_dirs = []

        if values is not None:
            log.debug('Set config exporter in directories "%s"' %
                      str(values))
            self._adp_dirs.extend(values)

    @property
    def mapper_in_dirs(self):
        return self._mapper_in_dirs

    def set_mapper_in_dirs(self, values):
        del self._mapper_in_dirs[:]
        self._mapper_in_dirs = []

        if values is not None:
            log.debug('Set config mapper in directories "%s"' %
                      str(values))
            self._mapper_in_dirs.extend(values)

    @property
    def loader_loop(self):
        return self._loader_loop

    @property
    def ondelivery_loop(self):
        return self._ondelivery_loop

    @property
    def reminder_loop(self):
        return self._reminder_loop

    @property
    def exporter_loop(self):
        return self._exporter_loop

    @property
    def mapper_loop(self):
        return self._mapper_loop

    @property
    def filter_loop(self):
        return self._filter_loop

    @property
    def adp_loop(self):
        return self._adp_loop

    @property
    def business_units(self):
        return self._business_units

    @property
    def t1250_file_format(self):
        return self._t1250_file_format

    @property
    def file_bu(self):
        return self._file_bu

    @property
    def support_emails(self):
        return self._support_emails

    def set_support_emails(self, values):
        del self._support_emails[:]
        self._support_emails = []

        if values is not None:
            self._support_emails.extend(values)
        log.debug('%s email.support "%s"' % (self.facility, values))

    @property
    def cond(self):
        return self._cond

    @property
    def rest(self):
        return self._rest

    @property
    def exporter_fields(self):
        return self._exporter_fields

    @property
    def pe_in_file_format(self):
        return self._pe_in_file_format

    @property
    def pe_in_file_archive_string(self):
        return self._pe_in_file_archive_string

    @property
    def pe_customer(self):
        return self._pe_customer

    @property
    def inbound_tcd(self):
        return self._inbound_tcd

    def set_inbound_tcd(self, values):
        del self._inbound_tcd[:]
        self._inbound_tcd = []

        if values is not None:
            self._inbound_tcd.extend(values)

    @property
    def tcd_filename_format(self):
        return self._tcd_filename_format

    @property
    def uncollected_day_range(self):
        return self._uncollected_day_range

    @property
    def file_cache_size(self):
        return self._file_cache_size

    def set_file_cache_size(self, value):
        self._file_cache_size = int(value)
        log.debug('Set primary_elect:file_cache_size to "%s"' %
                  self._file_cache_size)

    @property
    def filter_customer(self):
        return self._filter_customer

    def set_filter_customer(self, value):
        self._filter_customer = value

    @property
    def filtering_rules(self):
        return self._filtering_rules

    def set_filtering_rules(self, values):
        del self._filtering_rules[:]
        self._filtering_rules = []

        if values is not None:
            self._filtering_rules.extend(values)
            log.debug('Config set filtering_rules to "%s"' %
                      str(self._filtering_rules))

    @property
    def notification_delay(self):
        return self._notification_delay

    def set_notification_delay(self, value):
        self._notification_delay = value

    @property
    def start_date(self):
        return self._start_date

    def set_start_date(self, value):
        self._start_date = value

    @property
    def hold_period(self):
        return self._hold_period

    def set_hold_period(self, value):
        self._hold_period = value

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        try:
            self._dirs_to_check = self.get('dirs', 'in').split(',')
            log.debug('Loader directories to check %s' % str(self.in_dirs))

            self.set_mapper_in_dirs(self.get('dirs',
                                             'mapper_in').split(','))
            log.debug('Config mapper directories to check %s' %
                      str(self.mapper_in_dirs))

            self.set_archive_dir(self.get('dirs', 'archive'))

            self.set_staging_base(self.get('dirs', 'staging_base'))

            #self._signature = self.get('dirs', 'signature')
            #log.debug('Exporter signature directory %s' % self._signature)

            self._comms = self.get('dirs', 'comms')
            log.debug('Comms file directory %s' % self._comms)

            self._business_units = dict(self.items('business_units'))
            log.debug('Exporter Business Units %s' %
                      self._business_units.keys())

            self._file_bu = dict(self.items('file_bu'))
            log.debug('Exporter File Business Units %s' % self._file_bu)
        except ConfigParser.NoOptionError, err:
            log.critical('Missing required config: %s' % err)
            sys.exit(1)

        try:
            self.set_prod(self.get('environment', 'prod'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s environment.prod not defined.  Using "%s"' %
                      self.prod)

        try:
            self._t1250_file_format = self.get('files',
                                               't1250_file_format')
            log.debug('T1250 file format %s' % self.t1250_file_format)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default T1250 file format: %s' %
                      self.t1250_file_format)

        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Primary Elect file format: %s' %
                      self.pe_in_file_format)

        try:
            archive_string = self.get('primary_elect',
                                      'file_archive_string')

            self._pe_in_file_archive_string = archive_string
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Primary Elect archiving string: %s' %
                      self.pe_in_file_archive_string)

        try:
            self._pe_customer = self.get('primary_elect', 'customer')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Primary Elect customer: %s' %
                      self.pe_customer)

        try:
            self.set_inbound_tcd(self.get('dirs', 'tcd_in').split(','))
            log.debug('Inbound TCD directories %s' % str(self.inbound_tcd))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default TCD inbound directory: %s' %
                      self.inbound_tcd)

        try:
            self._tcd_filename_format = self.get('primary_elect',
                                                 'tcd_filename_format')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default TCD file format: %s' %
                      self.tcd_filename_format)

        try:
            uncollected_day_range = self.get('primary_elect',
                                             'uncollected_day_range')
            self._uncollected_day_range = float(uncollected_day_range)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default On Delivery day range: %s' %
                      self.uncollected_day_range)

        try:
            tmp_val = self.get('primary_elect', 'file_cache_size')
            self.set_file_cache_size(tmp_val)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default TCD file cache size: %s' %
                      self.file_cache_size)

        # Aggregator directories.
        try:
            agg_dirs = self.get('dirs', 'aggregator').split(',')
            self.set_aggregator_dirs(agg_dirs)
            log.debug('Aggregator directories %s' % self.aggregator_dirs)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Aggregator inbound directories: %s' %
                      self.aggregator_dirs)

        # ADP directories.
        try:
            tmp_vals = self.get('dirs', 'adp_in').split(',')
            self.set_adp_dirs(tmp_vals)
            log.debug('ADP in bound directories %s' % self.adp_dirs)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default ADP inbound directories: %s' %
                      self.adp_dirs)

        # Filter processing.
        try:
            self._filter_customer = self.get('filter', 'customer')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Filter customer: %s' %
                      self.filter_customer)
        try:
            tmp_vals = self.get('filter', 'fitering_rules')
            self._filtering_rules = tmp_vals.split(',')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Filtering rules: %s' %
                      self.filtering_rules)

        # Optional items (defaults provided).
        try:
            self.loader_loop = int(self.get('timeout', 'loader_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Loader loop: %d (sec)' %
                      self.loader_loop)

        try:
            self._ondelivery_loop = int(self.get('timeout',
                                                 'ondelivery_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default On Delivery loop: %d (sec)' %
                      self.ondelivery_loop)

        try:
            self._reminder_loop = int(self.get('timeout', 'reminder_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Reminder loop: %d (sec)' %
                      self.reminder_loop)

        try:
            self._exporter_loop = int(self.get('timeout', 'exporter_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Exporter loop: %d (sec)' %
                      self.exporter_loop)

        try:
            self._mapper_loop = int(self.get('timeout', 'mapper_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Mapper loop: %d (sec)' %
                      self.mapper_loop)

        try:
            self._filter_loop = int(self.get('timeout', 'filter_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Filter loop: %d (sec)' %
                      self.filter_loop)

        try:
            self._adp_loop = int(self.get('timeout', 'adp_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default ADP loop: %d (sec)' %
                      self.adp_loop)

        try:
            self._support_emails = self.get('email', 'support').split(',')
        except ConfigParser.NoOptionError, err:
            log.warn('%s emails not provided: %s' % err)

        # Business unit conditons.  No probs if they are missing -- will
        # just default to '0' (False) for each flag.
        try:
            self._cond = dict(self.items('conditions'))
            log.debug('Business Unit conditions %s' % self.cond.keys())
        except ConfigParser.NoSectionError, err:
            log.warn('Missing Business Unit conditions in config')

        # RESTful APIs.  May not need these if facility is not required
        # by any of the BU's
        try:
            self._rest = dict(self.items('rest'))
            log.debug('RESTful APIs %s' % str(self._rest))
        except ConfigParser.NoSectionError, err:
            log.warn('No RESTful APIs in config')

        # Exporter business unit-based column output and ordering.
        # Default is to simply display order as per query.
        try:
            self._exporter_fields = dict(self.items('exporter_fields'))
            log.debug('Exporter fields %s' % str(self._exporter_fields))
        except ConfigParser.NoSectionError, err:
            log.warn('No Exporter column output ordering in config')

        # Reminder notification_delay.
        try:
            notification_delay = self.get('reminder', 'notification_delay')
            self.set_notification_delay(int(notification_delay))
            log.debug('Parsed reminder notification delay: "%s"' %
                      notification_delay)
        except ConfigParser.NoOptionError, err:
            log.debug('Using default reminder notification delay: %d' %
                      self.notification_delay)

        # Reminder start_date.
        try:
            start_date = self.get('reminder', 'start_date')
            start_time = time.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.fromtimestamp(time.mktime(start_time))
            self.set_start_date(dt)
            log.debug('Parsed reminder start date: "%s"' % start_date)
        except ConfigParser.NoOptionError, err:
            log.debug('Using default reminder start date: %s' %
                      self.start_date)

        # Reminder hold_period.
        try:
            hold_period = self.get('reminder', 'hold_period')
            self.set_hold_period(int(hold_period))
            log.debug('Parsed reminder hold period: "%s"' % hold_period)
        except ConfigParser.NoOptionError, err:
            log.debug('Using default reminder hold period: %d' %
                      self.hold_period)

        # Transend.
        try:
            self._delivered_header = self.get('transsend',
                                              'delivered_header')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default delivered_header: %s' %
                      self.delivered_header)

        try:
            self._delivered_header = self.get('transsend',
                                              'delivered_event_key')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default delivered_event_key: %s' %
                      self.delivered_event_key)

        try:
            self._scan_desc_header = self.get('transsend',
                                              'scan_desc_header')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default scan_desc_header: %s' %
                      self.scan_desc_header)

        try:
            tmp_vals = self.get('transsend', 'scan_desc_keys')
            self._scan_desc_keys = tmp_vals.split(',')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default scan_desc_keys: %s' %
                      self.scan_desc_keys)

        for r in ['uncollected',
                  'compliance',
                  'noncompliance',
                  'exception',
                  'totals',
                  'collected']:
            report_opt = 'report_%s' % r

        # Health.
        try:
            health_procs = self.get('health', 'processes')
            self.set_health_processes(health_procs.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default health process list: %s' %
                      str(self.health_processes))

        # ADP headers
        try:
            self.set_adp_headers(dict(self.items('adp_headers')))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default ADP headers: %s' % self.adp_headers)

        # ADP file formats.
        try:
            tmp_vals = self.get('adp', 'file_formats')
            self.set_adp_file_formats(tmp_vals.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default ADP file formats: %s' %
                      str(self.adp_file_formats))

        # ADP file formats.
        try:
            self.set_code_header(self.get('adp', 'code_header'))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default DP code header: %s' %
                      str(self.code_header))

        # Delivery partners.
        try:
            tmp_vals = self.get('adp', 'delivery_partners')
            self.set_delivery_partners(tmp_vals.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default DP code header: %s' %
                      str(self.delivery_partners))

        # Delivery partner default passwords.
        try:
            tmp_vals = dict(self.items('adp_default_passwords'))
            self.set_adp_default_passwords(tmp_vals)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default delivery partner passwords: %s' %
                      str(self.adp_default_passwords))

    def condition(self, bu, flag):
        """Return the *bu* condition *flag* value.

        **Args:**
            *bu*: the name of the Business Unit.

            *flag*: name of the flag to process.

        **Returns:**
            boolean ``True`` if flag is '1'

            boolean ``False`` if flag is '0' or undefined

        """
        status = False

        if self.cond:
            index = FLAG_MAP.get(flag)
            if index is None:
                log.debug('Condition map undefined flag "%s"' % flag)
            else:
                if self.cond.get(bu) is None:
                    log.debug('Condition map missing BU "%s" option' % bu)
                else:
                    # Finally, get the flag!!!
                    try:
                        status = self.cond.get(bu)[index]
                        log.debug('Condition map %s:%s is "%s"' %
                                  (bu, flag, status))
                    except IndexError, e:
                        status = 0
        else:
            log.debug('Conditions config item is not defined')

        return status == '1'

    def comms_map(self, bu):
        """The comms trigger has become somewhat of a convoluted mess
        with various use-cases.  This method returns the *bu* based comms
        flags in a simpler dictionary lookup.

        **Args:**
            *bu*: the name of the Business Unit.  Only the first 4
            characters are accepted.  For example, ``tolf_nsw`` will be
            interpreted as ``tolf``.

        **Returns:**
            dictionary structure of the comms flags similar to::
                {'send_email': False,
                 'send_sms': True}

        """
        log.debug('Generating comms_map for Business Unit "%s"' % bu)

        comms_map = {'send_email': False,
                     'send_sms': False}

        for k in comms_map.keys():
            comms_map[k] = self.condition(bu, k)

        return comms_map

    def condition_map(self, bu):
        """Return the *bu* condition map values.

        **Args:**
            *bu*: the name of the Business Unit.  Only the first 4
            characters are accepted.  For example, ``tolf_nsw`` will be
            interpreted as ``tolf``.

        **Returns:**
            dict representing all of the condition flags for the *bu*

        """
        c_map = {}

        bu = bu[:4]
        for flag in FLAG_MAP.keys():
            status = self.condition(bu, flag)
            log.debug('bu/flag - status | %s/%s - %s' % (bu, flag, status))
            c_map[flag] = status

        return c_map

    def required_facility(self, flag):
        """Check the *flag* conditions as a set and return ``True`` if at
        least one of the flags is set.

        Verifies if the facility denoted by *flag* is a required component.

        **Args:**
            *flag*: the name of the flag as per the ``FLAG_MAP`` options to
            verify

        **Returns:**
            boolean ``True`` if any flag in the set is '1'

            boolean ``False`` if no flags in the set are '1'

        """
        log.debug('have facility check for flag %s' % flag)
        status = False

        if self.cond:
            for bu in self.cond.keys():
                if self.condition(bu, flag):
                    log.debug('Facility "%s" required by "%s"' %
                              (flag, bu))
                    status = True
                    break
        else:
            log.debug('Conditions config item is not defined')

        return status

    def get_pod_control(self, bu, type='xfer'):
        """Return the *bu* control settings from the condition map
        values based on *type*.

        Supported values for *type* include:

        * **xfer** - POD files to be sent to the outbound staging area
          or delete

        * **archive** - send to the archive directory

        **Args:**
            *bu*: the name of the Business Unit.

        **Kwargs:**
            *type*: distinguish between POD file transfer (**xfer**)
            or archiving (**archive**) (default ``xfer`` or file transfer)

        **Returns:**
            dictionary representing all of the file control condition flags
            for the *bu*.  For example, if Business Unit has a
            ``send_ps_file`` flag ``0`` and ``send_png_file`` flag ``1``::

                {'ps': False,
                 'png': True}

        """
        pod_control = {}

        if type == 'xfer':
            pod_control['ps'] = self.condition(bu, 'send_ps_file')
            pod_control['png'] = self.condition(bu, 'send_png_file')
        elif type == 'archive':
            pod_control['ps'] = self.condition(bu, 'archive_ps_file')
            pod_control['png'] = self.condition(bu, 'archive_png_file')

        return pod_control

    def bu_to_file(self, bu):
        """Return the file_bu configuration option of a given *bu*.

        State-based BU to file translations are not supported.  For
        example, ``tolf_vic``.

        **Args:**
            *bu*: business unit name as defined under the business_units
            section of the config.  For example, 'priority'.

        **Returns:**
            ``file_bu`` string such as ``TOLP``, ``TOLF`` or ``TOLI``

        """
        file_code_for_bu = None

        bu_value = self.business_units.get(bu)

        if bu_value is not None:
            for file_bu in self.file_bu.keys():
                if len(file_bu) > 4:
                    # Not interested in the state based BU's.
                    continue
                if self.file_bu.get(file_bu) == bu_value:
                    file_code_for_bu = file_bu
                    break

        return file_code_for_bu

    def bu_ids_with_set_condition(self, flag):
        """Given condition *flag*, will traverse the condition map for
        all Business Units and return the Business Unit IDs for the set
        flags.

        **Args:**
            *flag*: string-based condition map flag to check.  For example,
            ``pe_comms``

        **Returns:**
            tuple structure with the Business Unit ID's whose *flag* is
            set

        """
        log.debug('Getting BU ids for set "%s" condition' % flag)

        set_bu_ids = []
        for bu_name, id in self.business_units.iteritems():
            if self.condition(self.bu_to_file(bu_name), flag):
                set_bu_ids.append(int(id))

        set_bu_ids = tuple(sorted(set_bu_ids))
        log.debug('"%s" flag set BU ids: %s' % (flag, str(set_bu_ids)))

        return set_bu_ids

    @property
    def pe_comms_ids(self):
        return self.bu_ids_with_set_condition('pe_comms')

    @property
    def sc4_comms_ids(self):
        return self.bu_ids_with_set_condition('on_del_sc_4')

    def db_kwargs(self):
        """Extract database connectivity information from the config.

        Database connectivity information is taken from the ``[db]``
        section in the configuration file.  A typical example is::

            [db]
            driver = FreeTDS
            host = SQVDBAUT07
            database = Nparcel
            user = npscript
            password = <passwd>
            port =  1442

        Base assumptions on "host" keyword.  No "host" means this must be a
        test scenario in which case the database session is a memory-based
        sqlite instance.

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'driver': ...,
                          'host': ...,
                          'database': ...,
                          'user': ...,
                          'password': ...,
                          'port': ...}

        """
        kwargs = None

        try:
            host = self.get('db', 'host')
            driver = self.get('db', 'driver')
            database = self.get('db', 'database')
            user = self.get('db', 'user')
            password = self.get('db', 'password')
            port = self.get('db', 'port')
            if port is not None and port:
                port = int(port)
            kwargs = {'driver': driver,
                      'host': host,
                      'database': database,
                      'user': user,
                      'password': password,
                      'port': port}
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Missing DB key via config: %s' % err)

        return kwargs

    def ts_db_kwargs(self):
        """Extract TransSend database connectivity information from the
        config.

        Database connectivity information is taken from the
        ``[transsend_db]`` section in the configuration file.  A typical
        example is::

            [transsend_db]
            host = SIEDBDOD04
            user = nparcel
            password = <passwd>
            port = 1521
            sid = TRCOPUAT

        Base assumptions on "host" keyword.  No "host" means this must be a
        test scenario in which case the database session is a memory-based
        sqlite instance.

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'host': ...,
                          'user': ...,
                          'password': ...,
                          'port': ...,
                          'sid': ...}

        """
        kwargs = None

        try:
            host = self.get('transsend_db', 'host')
            user = self.get('transsend_db', 'user')
            password = self.get('transsend_db', 'password')
            port = self.get('transsend_db', 'port')
            if port is not None and port:
                port = int(port)
            sid = self.get('transsend_db', 'sid')
            kwargs = {'host': host,
                      'user': user,
                      'password': password,
                      'port': port,
                      'sid': sid}
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.info('Missing TransSend DB key via config: %s' % err)

        return kwargs

    def proxy_kwargs(self):
        """Extract proxy connectivity information from the configuration.

        Proxy connectivity information is taken from the ``[proxy]``
        section in the configuration file.  A typical example is::

            [proxy]
            host = itproxy-farm.toll.com.au
            user = <username>
            password = <passwd>
            port = 8080
            protocol = https

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'host': ...,
                          'user': ...,
                          'password': ...,
                          'port': ...,
                          'protocol': ...}

        """
        kwargs = None

        try:
            host = self.get('proxy', 'host')
            user = self.get('proxy', 'user')
            password = self.get('proxy', 'password')
            port = self.get('proxy', 'port')
            if port is not None and port:
                port = int(port)
            self._proxy_scheme = self.get('proxy', 'protocol')
            kwargs = {'host': host,
                      'user': user,
                      'password': password,
                      'port': port,
                      'protocol': self._proxy_scheme}
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.warn('Config proxy: %s' % err)

        return kwargs

    def proxy_string(self, kwargs=None):
        """Constructs a proxy string based on the *kwargs* dictionary
        structure or :attr:`proxy` attribute (in that order if *kwargs* is
        ``None``).

        **Kwargs:**
            *kwargs* as per the return value of the :meth:`proxy_kwargs`
            method

        **Returns:**
            string that could be fed directly into a HTTP/S header
            to handle proxy authentication in the request.  Example::

                http://loumar:<passwd>@auproxy-farm.toll.com.aus:8080

        """
        values = None
        if kwargs is not None:
            values = kwargs
        else:
            values = self.proxy_kwargs()

        proxy = None
        if values is not None:
            # Check if we have a username and password.
            if (values.get('user') is not None and
                values.get('password') is not None):
                proxy = ("%s:%s@" % (values.get('user'),
                                     values.get('password')))

            if values.get('host') is not None:
                proxy += values.get('host')

            if values.get('port') is not None:
                proxy += ':' + str(values.get('port'))

        return proxy

    @property
    def proxy_scheme(self):
        return self._proxy_scheme

    def set_proxy_scheme(self, value):
        self._proxy_scheme = value

    @property
    def sms_api_kwargs(self):
        """Extract SMS API information from the configuration.

        SMS API information is taken from the ``[rest]``
        section in the configuration file.  A typical example is::

            [rest]
            sms_api = https://api.esendex.com/v1.0/messagedispatcher
            sms_user = username
            sms_pw = password

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'api': ...,
                          'api_username': ...,
                          'api_password': ...}

        """
        kwargs = {'api': None,
                  'api_username': None,
                  'api_password': None}

        try:
            kwargs['api'] = self.get('rest', 'sms_api')
            kwargs['api_username'] = self.get('rest', 'sms_user')
            kwargs['api_password'] = self.get('rest', 'sms_pw')

        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.warn('Config proxy: %s' % err)

        return kwargs

    @property
    def email_api_kwargs(self):
        """Extract email API information from the configuration.

        Email API information is taken from the ``[rest]``
        section in the configuration file.  A typical example is::

            [rest]
            email_api = https://apps.cinder.co/tollgroup...
            email_user = username
            email_pw = password
            failed_email = loumar@tollgroup.com

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'api': ...,
                          'api_username': ...,
                          'api_password': ...,
                          'support': ...}

        """
        kwargs = {'api': None,
                  'api_username': None,
                  'api_password': None,
                  'support': None}

        try:
            kwargs['api'] = self.get('rest', 'email_api')
            kwargs['api_username'] = self.get('rest', 'email_user')
            kwargs['api_password'] = self.get('rest', 'email_pw')
            kwargs['support'] = self.get('rest', 'failed_email')

        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.warn('Config proxy: %s' % err)

        return kwargs

    @property
    def delivered_header(self):
        return self._delivered_header

    def set_delivered_header(self, value):
        self._delivered_header = value

    @property
    def delivered_event_key(self):
        return self._delivered_event_key

    def set_delivered_event_key(self, value):
        self._delivered_event_key = value

    @property
    def scan_desc_header(self):
        return self._scan_desc_header

    def set_scan_desc_header(self, value):
        self._scan_desc_header = value

    @property
    def scan_desc_keys(self):
        return self._scan_desc_keys

    def set_scan_desc_keys(self, values):
        del self._scan_desc_keys[:]
        self._scan_desc_keys = []

        if values is not None:
            self._scan_desc_keys.append(values)
            log.debug('Set scan_desc_keys to "%s"' %
                      str(self._scan_desc_keys))

    @property
    def health_processes(self):
        return self._health_processes

    def set_health_processes(self, values=None):
        del self._health_processes[:]
        self._health_processes = []

        if values is not None:
            self._health_processes.extend(values)
            log.debug('Config health check process list: "%s"' %
                      self.health_processes)

    @property
    def adp_headers(self):
        return self._adp_headers

    def set_adp_headers(self, values=None):
        self._adp_headers.clear()

        if values is not None:
            self._adp_headers = values
            log.debug('Config ADP headers set to: "%s"' %
                      self.adp_headers)
        else:
            log.debug('Cleared ADP headers')

    @property
    def adp_file_formats(self):
        return self._adp_file_formats

    def set_adp_file_formats(self, values=None):
        del self._adp_file_formats[:]
        self._adp_file_formats = []

        if values is not None:
            self._adp_file_formats.extend(values)
            log.debug('Config ADP file format list: "%s"' %
                      self.adp_file_formats)

    @property
    def code_header(self):
        return self._code_header

    def set_code_header(self, value=None):
        if value is not None:
            self.code_header = value
            log.debug('Config set code_header to: "%s"' %
                      self.code_header)

    @property
    def delivery_partners(self):
        return self._delivery_partners

    def set_delivery_partners(self, values=None):
        del self._delivery_partners[:]
        self._delivery_partners = []

        if values is not None:
            self._delivery_partners.extend(values)
            log.debug('Config delivery partners list: "%s"' %
                      self.delivery_partners)

    @property
    def adp_default_passwords(self):
        return self._adp_default_passwords

    def set_adp_default_passwords(self, values=None):
        self._adp_default_passwords.clear()

        if values is not None:
            self._adp_default_passwords = values
            log.debug('Config ADP default passwords: "%s"' %
                      self.adp_default_passwords)
