__all__ = [
    "ReporterB2CConfig",
]
#import sys
import ConfigParser

import nparcel
from nparcel.utils.log import log


class ReporterB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.ReporterB2CConfig` captures the configuration items
    required for the ``npreporter`` facility.

    .. attribute:: report_bu_ids

        dictionary mapping between Business Unit ID (``job.bu_id``
        column) and a human-readable format

    .. attribute:: report_outdir

        temporary working directory to where report files are
        staged to for further processing

    .. attribute:: report_outfile

        basename that is used to generate the report file

    .. attribute:: report_outfile_ts_format

        the date/time string to append to the outfile

    .. attribute:: report_extension

        outbound report filename extension

    .. attribute:: report_type_outfile

        basename that is used to generate the uncollected report file

    .. attribute:: report_type_display_hdrs

        list of ordered column headers to display in the uncollected report

    .. attribute:: report_type_widths

        map of aliased header names and prefered column width

    .. attribute:: report_type_ws

        map of worksheet related items

    .. attribute:: report_email_recipients

        list of email recipients

    .. attribute:: report_type_bu_based

        flag to denote if the reports are to be based on Business Unit

    .. attribute:: report_type_delivery_partners

        string based list of Delivery Partner names to limit result set
        against.  For example, ``['Nparcel', 'Toll']``.  The values
        supported are as per the ``delivery_partner.name`` table set

    .. attribute:: report_bu_id_recipients

        list of Business Unit specific recipients

    .. attribute:: report_compliance_period

        time (in days) from now that is the cut off for agent compliance
        (default 7 days)

    """
    _report_type = 'uncollected'
    _report_bu_ids = {}
    _report_outdir = '/data/nparcel/reports'
    _report_outfile = 'Report_'
    _report_outfile_ts_format = '%Y%m%d-%H:%M'
    _report_extension = 'xlsx'
    _report_type_outfile = None
    _report_type_display_hdrs = []
    _report_type_aliases = {}
    _report_type_widths = {}
    _report_type_ws = {}
    _report_type_recipients = []
    _report_type_bu_based = False
    _report_type_delivery_partners = []
    _report_bu_id_recipients = {}
    _report_compliance_period = 7

    def __init__(self, file=None, type=None):
        """ReporterB2CConfig initialisation.
        """
        nparcel.B2CConfig.__init__(self, file)

        if type is not None:
            self.set_report_type(type)

    @property
    def report_type(self):
        return self._report_type

    def set_report_type(self, value=None):
        self._report_type = value
        log.debug('%s report_type set to "%s"' %
                  (self.facility, self.report_type))

    @property
    def report_bu_ids(self):
        return self._report_bu_ids

    def set_report_bu_ids(self, values):
        self._report_bu_ids.clear()

        if values is not None:
            self._report_bu_ids = values
        log.debug('%s report_bu_ids set to "%s"' %
                  (self.facility, self._report_bu_ids))

    @property
    def report_outdir(self):
        return self._report_outdir

    def set_report_outdir(self, value):
        self._report_outdir = value
        log.debug('%s report_outdir set to "%s"' %
                  (self.facility, self._report_outdir))

    @property
    def report_outfile(self):
        return self._report_outfile

    def set_report_outfile(self, value):
        self._report_outfile = value
        log.debug('%s report_outfile set to "%s"' %
                  (self.facility, self._report_outfile))

    @property
    def report_outfile_ts_format(self):
        return self._report_outfile_ts_format

    def set_report_outfile_ts_format(self, value):
        self._report_outfile_ts_format = value
        log.debug('%s report_outfile_ts_format set to "%s"' %
                  (self.facility, self._report_outfile_ts_format))

    @property
    def report_extension(self):
        return self._report_extension

    def set_report_extension(self, value):
        self._report_extension = value
        log.debug('%s report_extension set to "%s"' %
                  (self.facility, self.report_extension))

    @property
    def report_type_outfile(self):
        return self._report_type_outfile

    def set_report_type_outfile(self, value):
        self._report_type_outfile = value
        log.debug('%s report_type_outfile set to "%s"' %
                  (self.facility, self.report_type_outfile))

    @property
    def report_type_display_hdrs(self):
        return self._report_type_display_hdrs

    def set_report_type_display_hdrs(self, values=None):
        del self.report_type_display_hdrs[:]
        self._report_type_display_hdrs = []

        if values is not None:
            self._report_type_display_hdrs.extend(values)
        log.debug('%s report_%s.display_hdrs set to "%s"' %
                  (self.facility,
                   self.report_type,
                   self.report_type_display_hdrs))

    @property
    def report_type_aliases(self):
        return self._report_type_aliases

    def set_report_type_aliases(self, values=None):
        self._report_type_aliases.clear()

        if values is not None:
            self._report_type_aliases = values
        log.debug('%s report_%s.aliases set to "%s"' %
                  (self.facility,
                   self.report_type,
                   self.report_type_aliases))

    @property
    def report_type_widths(self):
        return self._report_type_widths

    def set_report_type_widths(self, values=None):
        self._report_type_widths.clear()

        if values is not None:
            self._report_type_widths = values
        log.debug('%s report_%s_widths set to "%s"' %
                  (self.facility,
                   self.report_type,
                   self.report_type_widths))

    @property
    def report_type_ws(self):
        return self._report_type_ws

    def set_report_type_ws(self, values=None):
        self._report_type_ws.clear()

        if values is not None:
            self._report_type_ws = values
        log.debug('%s report_%s_ws set to "%s"' %
                  (self.facility,
                   self.report_type,
                   self.report_type_ws))

    @property
    def report_type_recipients(self):
        return self._report_type_recipients

    def set_report_type_recipients(self, values=None):
        del self._report_type_recipients[:]
        self._report_type_recipients = []

        if values is not None:
            self._report_type_recipients.extend(values)
        log.debug('%s report_%s.recipients set to "%s"' %
                  (self.facility,
                   self.report_type,
                   self.report_type_recipients))

    @property
    def report_type_delivery_partners(self):
        return self._report_type_delivery_partners

    def set_report_type_delivery_partners(self, values=None):
        del self._report_type_delivery_partners[:]
        self._report_type_delivery_partners = []

        if values is not None:
            self._report_type_delivery_partners.extend(values)
        log.debug('%s report_%s.delivery_partners set to "%s"' %
                  (self.facility,
                   self.report_type,
                   self.report_type_delivery_partners))

    @property
    def report_type_bu_based(self):
        return self._report_type_bu_based

    def set_report_type_bu_based(self, value=False):
        self.report_type_bu_based = (value.lower() == 'yes')
        log.debug('%s report_%s.bu_based flag set to "%s"' %
                  (self.facility,
                   self.report_type,
                   self.report_type_bu_based))

    @property
    def report_type_delivery_partners(self):
        return self._report_type_delivery_partners

    def set_report_type_delivery_partners(self, values=None):
        del self._report_type_delivery_partners[:]
        self._report_type_delivery_partners = []

        if values is not None:
            self._report_type_delivery_partners.extend(values)
        log.debug('%s report_%s.delivery_partners set to "%s"' %
                  (self.facility,
                   self.report_type,
                   self.report_type_delivery_partners))

    @property
    def report_bu_id_recipients(self):
        return self._report_bu_id_recipients

    def set_report_bu_id_recipients(self, values=None):
        self._report_bu_id_recipients.clear()

        if values is not None:
            self._report_bu_id_recipients = values
        log.debug('%s report_bu_id_recipients set to "%s"' %
                    (self.facility, self.report_bu_id_recipients))

    @property
    def report_compliance_period(self):
        return self._report_compliance_period

    def set_report_compliance_period(self, value):
        self.report_compliance_period = value
        log.debug('%s report_compliance_period: %s' %
                  (self.facility, self.report_compliance_period))

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        # These are the generic values that can be removed
        # after nparcel.B2CConfig is refactored.
        try:
            self.set_prod(self.get('environment', 'prod'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s environment.prod not in config: %s. Using "%s"' %
                      (self.facility, err, self.prod))

        # Exporter specific.
        try:
            bu_ids = dict(self.items('report_bu_ids'))
            tmp_bu_ids = {}
            for k, v in bu_ids.iteritems():
                tmp_bu_ids[int(k)] = v
            self.set_report_bu_ids(tmp_bu_ids)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s report_bu_ids: %s. Using "%s"' %
                      (self.facility, err, self.report_bu_ids))

        try:
            self.set_report_outdir(self.get('report_base', 'outdir'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s report_base.outdir: %s. Using "%s"' %
                      (self.facility, err, self.report_outdir))

        try:
            self.set_report_outfile(self.get('report_base', 'outfile'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s report_base.outfile: %s. Using "%s"' %
                      (self.facility, err, self.report_outfile))

        try:
            tmp = self.get('report_base', 'outfile_ts_format')
            self.set_report_outfile_ts_format(tmp)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s report_base.outfile_ts_format: %s. Using "%s"' %
                      (self.facility, err, self.report_outfile_ts_format))

        try:
            self.set_report_extension(self.get('report_base', 'extension'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s report_base.extension: %s. Using "%s"' %
                      (self.facility, err, self.report_extension))

        report_section = 'report_%s' % self.report_type
        for attr in ['outfile',
                     'display_hdrs',
                     'recipients',
                     'bu_based',
                     'delivery_partners']:
            getter = 'report_type_%s' % attr
            get_method = getattr(self, getter)
            setter = 'set_%s' % getter
            set_method = getattr(self, setter)
            try:
                val = self.get(report_section, attr)
                if attr in ['display_hdrs',
                            'recipients',
                            'delivery_partners']:
                    set_method(val.split(','))
                else:
                    set_method(val)
            except (ConfigParser.NoOptionError,
                    ConfigParser.NoSectionError), err:
                log.debug('%s report_%s.%s: %s. Using "%s"' %
                          (self.facility,
                           self.report_type,
                           attr,
                           err,
                           get_method))

        for attr in ['aliases',
                     'widths',
                     'ws']:
            report_section = 'report_%s_%s' % (self.report_type, attr)
            getter = 'report_type_%s' % attr
            get_method = getattr(self, getter)
            setter = 'set_%s' % getter
            set_method = getattr(self, setter)
            try:
                val = dict(self.items(report_section))
                tmp_val = {}
                for k, v in val.iteritems():
                    if attr == 'aliases':
                        tmp_val[k.upper()] = v
                    elif attr == 'widths':
                        tmp_val[k.lower()] = int(v)
                    else:
                        tmp_val[k] = v
                set_method(tmp_val)
            except (ConfigParser.NoOptionError,
                    ConfigParser.NoSectionError), err:
                log.debug('%s report_%s_%s: %s. Using "%s"' %
                          (self.facility,
                           self.report_type,
                           attr,
                           err,
                           get_method))

        try:
            bu_recipients = dict(self.items('report_bu_id_recipients'))
            tmp_recipients = {}
            for k, v in bu_recipients.iteritems():
                tmp_recipients[int(k)] = v.split(',')
            bu_recipients = tmp_recipients
            self.set_report_bu_id_recipients(bu_recipients)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s report_bu_id_recipients: %s. Using %s' %
                      (self.facility,
                       err,
                       self.report_bu_id_recipients))

        # Report specific options.
        if self.report_type == 'compliance':
            try:
                tmp_period = self.get('report_compliance', 'period')
                self.set_report_compliance_period(int(tmp_period))
            except (ConfigParser.NoOptionError,
                    ConfigParser.NoSectionError), err:
                msg = ('%s report_compliance.period: %s' %
                       (self.facility, self.report_compliance_period))
                log.debug(msg)
