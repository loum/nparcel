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
            'on_del_sc_4': 14}


class B2CConfig(nparcel.Config):
    """Nparcel Config class.

    :class:`nparcel.Config` captures the configuration items required
    by the Nparcel B2C Replicator.

    .. attribute:: dirs_to_check (loader)

        list of directories to look for T1250 files.

    .. attribute:: archive

        directory to place processed T1250 files into.

    .. attribute:: staging_base (exporter)

        directory to place processed collected reports and signature files
        for further processing.

    .. attribute:: signature (exporter)

        directory where POD signature files are kept.

    .. attribute:: comms (loader, primary elect)

        directory where comms files are kept for further processing

    .. attribute:: aggregators (ParcelPoint processing)

        directory where T1250 loader files are aggregated for further
        processing

    .. attribute loader_loop (loader)

        time (seconds) between loader processing iterations.

    .. attribute onleilvery_loop (on delivery)

        time (seconds) between on delivery processing iterations.

    .. attribute reminder_loop (reminder)

        time (seconds) between primary elect processing iterations.

    .. attribute comms_loop (comms)

        time (seconds) between notification iterations.

    .. attribute:: exporter_loop (exporter)

        time (seconds) between exporter processing iterations.

    .. attribute:: mapper_loop (exporter)

        time (seconds) between mapper processing iterations.

    .. attribute:: filter_loop (exporter)

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

    .. attribute:: skip_days (comms)

        list of days ['Saturday', 'Sunday'] to not send messages

    .. attribute:: send_time_ranges (comms)

        time ranges when comms can be sent

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

    .. attribute:: pe_inbound_mts

        MTS Delivery Report inbound directory
        (default ``/data/nparcel/mts``)

    .. attribute:: pe_mts_filename_format

        regular expression format string for Primary Elect MTS delivery
        reports inbound filenames
        (default ``mts_delivery_report_\d{14}\.csv``)

    .. attribute:: filter_customer

        downstream recipient of filtered T1250 files
        (default ``parcelpoint``)

    .. attribute:: delivered_header

        string that represents the TransSend column header name for
        a delivered item (default ``latest_scan_event_action``)

    .. attribute:: delivered_event_key

        string that represents a delivered event
        (default ``delivered``)

    .. attribute:: report_bu_ids

        dictionary mapping between Business Unit ID (``job.bu_id``
        column) and a human-readable format

    .. attribute:: report_outfile

        basename that is used to generate the report file

    .. attribute:: report_outdir

        temporary working directory to where report files are
        staged to for further processing

    .. attribute:: report_extension

        report filename extension

    .. attribute:: report_outfile (uncollected)

        basename that is used to generate the uncollected report file

    .. attribute:: report_uncollected_display_hdrs

        list of ordered column headers to display in the uncollected report

    .. attribute:: report_uncollected_aliases

        map of raw header names and the preferred name to display in
        report

    .. attribute:: report_uncollected_widths

        map of aliased header names and prefered column width

    .. attribute:: report_uncollected_ws

        map of worksheet related items

    .. attribute:: report_uncollected_recipients

        list of email recipients

    .. attribute:: report_uncollected_bu_based

        flag to denote if the reports are to be based on Business Unit

    .. attribute:: report_bu_id_recipients

        list of Business Unit specific recipients

    """
    _dirs_to_check = []
    _pe_dirs_to_check = []
    _archive = None
    _staging_base = None
    _signature = None
    _comms = None
    _aggregator_dirs = []
    _loader_loop = 30
    _ondelivery_loop = 30
    _reminder_loop = 3600
    _comms_loop = 30
    _exporter_loop = 300
    _mapper_loop = 30
    _filter_loop = 30
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
    _skip_days = ['Sunday']
    _send_time_ranges = ['08:00-19:00']
    _comms_q_warning = 100
    _comms_q_error = 1000
    _exporter_fields = {}
    _pe_in_file_format = 'T1250_TOL[PIF]_\d{14}\.dat'
    _pe_in_file_archive_string = 'T1250_TOL[PIF]_(\d{8})\d{6}\.dat'
    _pe_customer = 'gis'
    _pe_inbound_mts = ['/data/nparcel/mts']
    _pe_mts_filename_format = 'mts_delivery_report_\d{14}\.csv'
    _filter_customer = 'parcelpoint'
    _delivered_header = 'latest_scan_event_action'
    _delivered_event_key = 'delivered'
    _report_bu_ids = {}
    _report_outfile = 'Report_'
    _report_outfile_ts_format = '%Y%m%d-%H:%M'
    _report_outdir = '/data/nparcel/reports'
    _report_extension = 'xlsx'
    _report_uncollected_outfile = 'Stocktake_uncollected_aged_report_'
    _report_uncollected_display_hdrs = []
    _report_uncollected_aliases = {}
    _report_uncollected_widths = {}
    _report_uncollected_ws = {}
    _report_uncollected_recipients = []
    _report_uncollected_bu_based = False
    _report_bu_id_recipients = {}

    def __init__(self, file=None):
        """Nparcel Config initialisation.
        """
        nparcel.Config.__init__(self, file)

    @property
    def in_dirs(self):
        return self._dirs_to_check

    def set_in_dirs(self, values):
        del self._dirs_to_check[:]

        if values is not None:
            log.debug('Set inbound directory "%s"' % str(values))
            self._dirs_to_check.extend(values)
        else:
            self._dirs_to_check = []

    @property
    def pe_in_dirs(self):
        return self._pe_dirs_to_check

    def set_pe_in_dirs(self, values):
        del self._pe_dirs_to_check[:]

        if values is not None:
            log.debug('Set PE in directory "%s"' % str(values))
            self._pe_dirs_to_check.extend(values)
        else:
            self._send_time_ranges = []

    @property
    def archive_dir(self):
        return self._archive

    def set_archive_dir(self, value):
        self._archive = value
        log.debug('Set archive directory to "%s"' % self._archive)

    @property
    def staging_base(self):
        return self._staging_base

    @property
    def signature_dir(self):
        return self._signature

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

        if values is not None:
            log.debug('Set config aggregator in directories "%s"' %
                      str(values))
            self._aggregator_dirs.extend(values)
        else:
            self._aggregator_dirs = []

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
    def comms_loop(self):
        return self._comms_loop

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

        if values is not None:
            log.debug('Set Support Emails "%s"' % str(values))
            self._support_emails.extend(values)
        else:
            self._support_emails = []

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
    def pe_inbound_mts(self):
        return self._pe_inbound_mts

    def set_pe_inbound_mts(self, values):
        del self._pe_inbound_mts[:]
        self._pe_inbound_mts = []

        if values is not None:
            self._pe_inbound_mts.extend(values)

    @property
    def pe_mts_filename_format(self):
        return self._pe_mts_filename_format

    @property
    def filter_customer(self):
        return self._filter_customer

    def set_filter_customer(self, value):
        self._filter_customer = value

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

    @property
    def skip_days(self):
        return self._skip_days

    def set_skip_days(self, values):
        del self._skip_days[:]

        if values is not None:
            log.debug('Set skip days to "%s"' % str(values))
            self._skip_days.extend(values)
        else:
            self._skip_days = []

    @property
    def send_time_ranges(self):
        return self._send_time_ranges

    def set_send_time_ranges(self, values):
        del self._send_time_ranges[:]

        if values is not None:
            log.debug('Set send time ranges "%s"' % str(values))
            self._send_time_ranges.extend(values)
        else:
            self._send_time_ranges = []

    @property
    def comms_q_warning(self):
        return self._comms_q_warning

    def set_comms_q_warning(self, value):
        self._comms_q_warning = value

    @property
    def comms_q_error(self):
        return self._comms_q_error

    def set_comms_q_error(self, value):
        self._comms_q_error = value

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        try:
            self._dirs_to_check = self.get('dirs', 'in').split(',')
            log.debug('Loader directories to check %s' % str(self.in_dirs))

            self._archive = self.get('dirs', 'archive')
            log.debug('Loader archive directory %s' % self._archive)

            self._staging_base = self.get('dirs', 'staging_base')
            log.debug('Exporter staging base %s' % self._staging_base)

            self._signature = self.get('dirs', 'signature')
            log.debug('Exporter signature directory %s' % self._signature)

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

        # The standard T1250 file (which shouldn't change much)
        try:
            self._t1250_file_format = self.get('files',
                                               't1250_file_format')
            log.debug('T1250 file format %s' % self.t1250_file_format)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default T1250 file format: %s' %
                      self.t1250_file_format)

        # Primary elect work is only a temporary solution.
        try:
            self._pe_dirs_to_check = self.get('dirs', 'pe_in').split(',')
            log.debug('Primary Elect directories to check %s' %
                      str(self.pe_in_dirs))
        except ConfigParser.NoOptionError:
            log.warn('No Primary Elect inbound directories in config')

        try:
            self._pe_in_file_format = self.get('primary_elect',
                                               'file_format')
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
            self.set_pe_inbound_mts(self.get('primary_elect',
                                             'inbound_mts').split(','))
            log.debug('Primary Elect directories to check %s' %
                      str(self.pe_in_dirs))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Primary Elect MTS directory: %s' %
                      self.pe_inbound_mts)

        try:
            self._pe_mts_filename_format = self.get('primary_elect',
                                                    'mts_filename_format')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Primary Elect MTS file format: %s' %
                      self.pe_mts_filename_format)

        # Aggregator.
        try:
            agg_dirs = self.get('dirs', 'aggregator').split(',')
            self.set_aggregator_dirs(agg_dirs)
            log.debug('Aggregator directories %s' % self.aggregator_dirs)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Aggregator inbound directories: %s' %
                      self.aggregator_dirs)

        # Filter processing.
        try:
            self._filter_customer = self.get('filter', 'customer')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Filter customer: %s' %
                      self.filter_customer)

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
            self._comms_loop = int(self.get('timeout', 'comms_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Notifications loop: %d (sec)' %
                      self.comms_loop)

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
            self._support_emails = self.get('email', 'support').split(',')
        except ConfigParser.NoOptionError, err:
            log.warn('Support emails not provided: %s' % err)

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

        # Comms skip_days.
        try:
            skip_days = self.get('comms', 'skip_days').split(',')
            self.set_skip_days(skip_days)
            log.debug('Parsed comms days to skip: "%s"' % skip_days)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default skip_days: %s' % str(self.skip_days))

        # Comms send_time_ranges.
        try:
            send_time_ranges = self.get('comms', 'send_time_ranges')
            self.set_send_time_ranges(send_time_ranges.split(','))
            log.debug('Parsed comms send time ranges: "%s"' %
                      send_time_ranges)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default send time ranges: %s' %
                      str(self.send_time_ranges))

        # Comms comms queue warning threshold.
        try:
            comms_q_warning = self.get('comms', 'comms_queue_warning')
            self.set_comms_q_warning(int(comms_q_warning))
            log.debug('Parsed comms queue warn threshold: "%s"' %
                      comms_q_warning)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default comms queue warning: %s' %
                      self.comms_q_warning)

        # Comms comms queue error threshold.
        try:
            comms_q_error = self.get('comms', 'comms_queue_error')
            self.set_comms_q_error(int(comms_q_error))
            log.debug('Parsed comms queue error threshold: "%s"' %
                      comms_q_error)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default comms queue error: %s' %
                      self.comms_q_error)

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

        # Reporter.
        try:
            bu_ids = dict(self.items('report_bu_ids'))
            tmp_bu_ids = {}
            for k, v in bu_ids.iteritems():
                tmp_bu_ids[int(k)] = v
            self.set_report_bu_ids(tmp_bu_ids)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report_bu_ids: %s' %
                      self.report_bu_ids)

        try:
            self.set_report_outfile(self.get('report_base', 'outfile'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report outfile: %s' %
                      self.report_outfile)

        try:
            self.set_report_outfile_ts_format(self.get('report_base',
                                                       'outfile_ts_format'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report outfile_ts_format: %s' %
                      self.report_outfile_ts_format)

        try:
            self.set_report_outdir(self.get('report_base', 'outdir'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report outdir: %s' %
                      self.report_outdir)

        try:
            self.set_report_extension(self.get('report_base', 'extension'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report extension: %s' %
                      self.report_extension)

        try:
            display_hdrs = self.get('report_uncollected', 'display_hdrs')
            display_hdrs_list = display_hdrs.split(',')
            self.set_report_uncollected_display_hdrs(display_hdrs_list)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            msg = ('Using default report (uncollected) display hdrs: %s' %
                    self.report_extension)
            log.debug(msg)

        try:
            tmp_outfile = self.get('report_uncollected', 'outfile')
            self.set_report_uncollected_outfile(tmp_outfile)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report (uncollected) outfile: %s' %
                      self.report_uncollected_outfile)

        try:
            aliases = dict(self.items('report_uncollected_aliases'))
            tmp_aliases = {}
            for k, v in aliases.iteritems():
                tmp_aliases[k.upper()] = v
            aliases = tmp_aliases
            self.set_report_uncollected_aliases(aliases)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report uncollected aliases: %s' %
                      self.report_uncollected_aliases)

        try:
            widths = dict(self.items('report_uncollected_widths'))
            tmp_widths = {}
            for k, v in widths.iteritems():
                tmp_widths[k] = int(v)
            widths = tmp_widths
            self.set_report_uncollected_widths(widths)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report uncollected widths: %s' %
                      self.report_uncollected_widths)

        try:
            ws = dict(self.items('report_uncollected_ws'))
            self.set_report_uncollected_ws(ws)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report uncollected worksheets: %s' %
                      self.report_uncollected_ws)

        try:
            recipients = self.get('report_uncollected', 'recipients')
            recipients = recipients.split(',')
            self.set_report_uncollected_recipients(recipients)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            msg = ('Using default report (uncollected) recipients: %s' %
                    self.report_uncollected_recipients)
            log.debug(msg)

        try:
            tmp_bu_based = self.get('report_uncollected', 'bu_based')
            self.set_report_uncollected_bu_based(tmp_bu_based)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            msg = ('Using default report (uncollected) BU-based flag: %s' %
                    self.report_uncollected_bu_based)
            log.debug(msg)

        try:
            bu_recipients = dict(self.items('report_bu_id_recipients'))
            tmp_recipients = {}
            for k, v in bu_recipients.iteritems():
                tmp_recipients[int(k)] = v.split(',')
            bu_recipients = tmp_recipients
            self.set_report_bu_id_recipients(bu_recipients)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default report BU ID recipients: %s' %
                      self.report_bu_id_recipients)

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

    def get_file_control(self, bu):
        """Return the *bu* file control settings from the condition map
        values.

        **Args:**
            *bu*: the name of the Business Unit.

        **Returns:**
            dictionary representing all of the file control condition flags
            for the *bu*.  For example, if Business Unit has a
            ``send_ps_file`` flag ``0`` and ``send_png_file`` flag ``1``::

                {'ps': False,
                 'png': True}

        """
        file_control = {}

        file_control['ps'] = self.condition(bu, 'send_ps_file')
        file_control['png'] = self.condition(bu, 'send_png_file')

        return file_control

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
        except ConfigParser.NoOptionError, err:
            log.info('Missing DB key via config: %s' % err)

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

                http://loumar:<passwd>@itproxy-farm.toll.com.aus:8080

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
    def report_bu_ids(self):
        return self._report_bu_ids

    def set_report_bu_ids(self, values):
        self._report_bu_ids.clear()

        if values is not None:
            self._report_bu_ids = values
            log.debug('Set report_bu_ids to "%s"' % self._report_bu_ids)
        else:
            log.debug('Cleared report_bu_ids')

    @property
    def report_outfile(self):
        return self._report_outfile

    def set_report_outfile(self, value):
        self._report_outfile = value
        log.debug('Set report outfile to "%s"' % self._report_outfile)

    @property
    def report_outfile_ts_format(self):
        return self._report_outfile_ts_format

    def set_report_outfile_ts_format(self, value):
        self._report_outfile_ts_format = value
        log.debug('Set report outfile_ts_format to "%s"' %
                  self._report_outfile_ts_format)

    @property
    def report_outdir(self):
        return self._report_outdir

    def set_report_outdir(self, value):
        self._report_outdir = value
        log.debug('Set report outbound directory to "%s"' %
                  self._report_outdir)

    @property
    def report_extension(self):
        return self._report_extension

    def set_report_extension(self, value):
        self._report_extension = value
        log.debug('Set report extension to "%s"' % self.report_extension)

    @property
    def report_uncollected_outfile(self):
        return self._report_uncollected_outfile

    def set_report_uncollected_outfile(self, value):
        self._report_uncollected_outfile = value
        log.debug('Set report (uncollected) outfile to "%s"' %
                  self.report_uncollected_outfile)

    @property
    def report_uncollected_display_hdrs(self):
        return self._report_uncollected_display_hdrs

    def set_report_uncollected_display_hdrs(self, values=None):
        del self.report_uncollected_display_hdrs[:]
        self._report_uncollected_display_hdrs

        if values is not None:
            self._report_uncollected_display_hdrs.extend(values)
            log.debug('Setting (uncollected) headers to display to "%s"' %
                      self.report_uncollected_display_hdrs)
        else:
            log.debug('Clearing (uncollected) headers to display list')

    @property
    def report_uncollected_aliases(self):
        return self._report_uncollected_aliases

    def set_report_uncollected_aliases(self, values=None):
        self._report_uncollected_aliases.clear()

        if values is not None:
            self._report_uncollected_aliases = values
            log.debug('Set report uncollected aliases to "%s"' %
                      self.report_uncollected_aliases)
        else:
            log.debug('Cleared report uncollected aliases')

    @property
    def report_uncollected_widths(self):
        return self._report_uncollected_widths

    def set_report_uncollected_widths(self, values=None):
        self._report_uncollected_widths.clear()

        if values is not None:
            self._report_uncollected_widths = values
            log.debug('Set report uncollected widths to "%s"' %
                      self.report_uncollected_widths)
        else:
            log.debug('Cleared report uncollected widths')

    @property
    def report_uncollected_ws(self):
        return self._report_uncollected_ws

    def set_report_uncollected_ws(self, values=None):
        self._report_uncollected_ws.clear()

        if values is not None:
            self._report_uncollected_ws = values
            log.debug('Set report uncollected ws to "%s"' %
                      self.report_uncollected_ws)
        else:
            log.debug('Cleared report uncollected worksheet')

    @property
    def report_uncollected_recipients(self):
        return self._report_uncollected_recipients

    def set_report_uncollected_recipients(self, values=None):
        del self._report_uncollected_recipients[:]
        self._report_uncollected_recipients

        if values is not None:
            self._report_uncollected_recipients.extend(values)
            log.debug('Setting report uncollected recipients to "%s"' %
                      self.report_uncollected_recipients)
        else:
            log.debug('Clearing uncollected recipients list')

    @property
    def report_uncollected_bu_based(self):
        return self._report_uncollected_bu_based

    def set_report_uncollected_bu_based(self, value=False):
        self.report_uncollected_bu_based = (value == True)
        log.debug('Setting report uncollected BU-based flag to "%s"' %
                  self.report_uncollected_bu_based)

    @property
    def report_bu_id_recipients(self):
        return self._report_bu_id_recipients

    def set_report_bu_id_recipients(self, values=None):
        self._report_bu_id_recipients.clear()

        if values is not None:
            self._report_bu_id_recipients = values
            log.debug('Set report BU ID recipients to "%s"' %
                      self.report_bu_id_recipients)
        else:
            log.debug('Cleared report BU ID recipients')
