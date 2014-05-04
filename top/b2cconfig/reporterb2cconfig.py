__all__ = [
    "ReporterB2CConfig",
]
#import sys

import top
from top.utils.log import log
from top.utils.setter import (set_scalar,
                              set_list,
                              set_dict)


class ReporterB2CConfig(top.B2CConfig):
    """:class:`top.ReporterB2CConfig` captures the configuration items
    required for the ``topreporter`` facility.

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
    _report_outdir = '/data/top/reports'
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

    @property
    def report_type(self):
        return self._report_type

    @set_scalar
    def set_report_type(self, value=None):
        pass

    @property
    def report_bu_ids(self):
        return self._report_bu_ids

    @set_dict
    def set_report_bu_ids(self, values):
        pass

    @property
    def report_outdir(self):
        return self._report_outdir

    @set_scalar
    def set_report_outdir(self, value):
        pass

    @property
    def report_outfile(self):
        return self._report_outfile

    @set_scalar
    def set_report_outfile(self, value):
        pass

    @property
    def report_outfile_ts_format(self):
        return self._report_outfile_ts_format

    @set_scalar
    def set_report_outfile_ts_format(self, value):
        pass

    @property
    def report_extension(self):
        return self._report_extension

    @set_scalar
    def set_report_extension(self, value):
        pass

    @property
    def report_type_outfile(self):
        return self._report_type_outfile

    @set_scalar
    def set_report_type_outfile(self, value):
        pass

    @property
    def report_type_display_hdrs(self):
        return self._report_type_display_hdrs

    @set_list
    def set_report_type_display_hdrs(self, values=None):
        pass

    @property
    def report_type_aliases(self):
        return self._report_type_aliases

    @set_dict
    def set_report_type_aliases(self, values=None):
        pass

    @property
    def report_type_widths(self):
        return self._report_type_widths

    @set_dict
    def set_report_type_widths(self, values=None):
        pass

    @property
    def report_type_ws(self):
        return self._report_type_ws

    @set_dict
    def set_report_type_ws(self, values=None):
        pass

    @property
    def report_type_recipients(self):
        return self._report_type_recipients

    @set_list
    def set_report_type_recipients(self, values=None):
        pass

    @property
    def report_type_delivery_partners(self):
        return self._report_type_delivery_partners

    @set_list
    def set_report_type_delivery_partners(self, values=None):
        pass

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

    @set_list
    def set_report_type_delivery_partners(self, values=None):
        pass

    @property
    def report_bu_id_recipients(self):
        return self._report_bu_id_recipients

    @set_dict
    def set_report_bu_id_recipients(self, values=None):
        pass

    @property
    def report_compliance_period(self):
        return self._report_compliance_period

    @set_scalar
    def set_report_compliance_period(self, value):
        pass

    def __init__(self, file=None, type=None):
        """ReporterB2CConfig initialisation.
        """
        top.B2CConfig.__init__(self, file)

        if type is not None:
            self.set_report_type(type)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        top.Config.parse_config(self)

        kwargs = [{'section': 'report_base',
                   'option': 'outdir',
                   'var': 'report_outdir'},
                  {'section': 'report_base',
                   'option': 'outfile',
                   'var': 'report_outfile'},
                  {'section': 'report_base',
                   'option': 'outfile_ts_format',
                   'var': 'report_outfile_ts_format'},
                  {'section': 'report_base',
                   'option': 'extension',
                   'var': 'report_extension'}]

        report_section = 'report_%s' % self.report_type
        for attr in ['outfile',
                     'display_hdrs',
                     'recipients',
                     'bu_based',
                     'delivery_partners']:
            report_attr = 'report_type_%s' % attr
            if attr in ['display_hdrs',
                        'recipients',
                        'delivery_partners']:
                kwargs.append({'section': report_section,
                               'option': attr,
                               'var': 'report_type_%s' % attr,
                               'is_list': True})
            else:
                kwargs.append({'section': report_section,
                               'option': attr,
                               'var': 'report_type_%s' % attr})

        # Report specific options.
        if self.report_type == 'compliance':
            kwargs.append({'section': 'report_compliance',
                           'option': 'period',
                           'var': 'report_compliance_period',
                           'cast_type': 'int'})

        for kw in kwargs:
            self.parse_scalar_config(**kw)

        del kwargs[:]
        kwargs = [{'section': 'report_bu_ids',
                   'key_cast_type': 'int'},
                  {'section': 'report_bu_id_recipients',
                   'is_list': True,
                   'key_cast_type': 'int'},
                  {'section': '%s_aliases' % (report_section),
                   'var': 'report_type_aliases',
                   'key_case': 'upper'},
                  {'section': '%s_widths' % (report_section),
                   'var': 'report_type_widths',
                   'key_case': 'lower',
                   'cast_type': 'int'},
                  {'section': '%s_ws' % (report_section),
                   'var': 'report_type_ws'}]

        for kw in kwargs:
            self.parse_dict_config(**kw)
