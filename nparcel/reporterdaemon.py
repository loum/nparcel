__all__ = [
    "ReporterDaemon",
]
import os
import signal
import datetime

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import create_dir


class ReporterDaemon(nparcel.DaemonService):
    """Daemoniser facility for the reporting classes.

    .. attribute:: *bu_ids*

        dictionary mapping between Business Unit ID (``job.bu_id``
        column) and a human-readable format.  The default is::

            {1: 'Toll Priority',
             2: 'Toll Fast',
             3: 'Toll IPEC'}

    .. attribute:: *outfile*

        output filename base
        (default ``Stocktake_uncollected_aged_report_``)

    .. attribute:: *outfile_ts_format*

        timestamp format to append to the *outfile*
        (default ``%Y%m%d-%H%M``)

    .. attribute:: *outdir*

        temporary working directory to where report files are
        staged to for further processing (default ``/data/nparcel/reports``)

    .. attribute:: *extension*

        report filename extension

    .. attribute:: *display_hdrs*

        list of column headers to display in the report
        This can control the order and appearance of the raw query column
        set

    .. attribute:: *aliases*

        dictionary of raw header names and the preferred alias
        to display in the report.  For example::

            {'DP_CODE': 'Agent',
             'AGENT_NAME': 'Agent Name',
             'JOB_BU_ID': 'Business Unit',
             'CONNOTE_NBR': 'Connote',
             'ITEM_NBR': 'Item Nbr',
             'PIECES': 'Pieces'}

    .. attribute:: *header_widths*

        dictionary of aliased header names and prefered column width.
        For example::

                {'Agent Name': 30,
                 'Connote': 40,
                 'Item Nbr': 50,
                 'To': 30}

    .. attribute:: *ws*

        dictionary of values to represent within the Excel worksheet.
        Notable values include::

            {'title': ...
             'subtitle': ...
             'sheet_title': ...}

    .. attribute:: *report_filename*

        the generated report filename

    .. attribute:: *recipients*

        list of email recipients

    .. attribute:: *bu_id_recipients*

        dictionary of Business Unit IDs and their email recipeints for
        finer-grained controlled of reporting query.  For example,
        uncollected reports are run on a per-BU basis

    .. attribute:: *bu_based*

        boolean flag to run the report query on a per-Business Unit basis

    .. attribute:: *delivery_partners*

        list of Agent Delivery Partners to limit query set against

    .. attribute:: *compliance_period*

        time (in days) from now that is the cut off for agent compliance
        (default 7 days)

    """
    _report_type = None
    _config = None
    _report = None
    _bu_ids = {}
    _outdir = os.path.join(os.sep, 'data', 'nparcel', 'reports')
    _outfile = 'Stocktake_uncollected_aged_report_'
    _outfile_ts_format = '%Y%m%d-%H:%M'
    _extension = 'xlsx'
    _display_hdrs = []
    _aliases = {}
    _header_widths = {}
    _ws = {'title': str(),
           'sub_title': str(),
           'sheet_title': str()}
    _report_filename = None
    _recipients = []
    _bu_id_recipients = {}
    _bu_based = False
    _delivery_partners = []
    _compliance_period = 7
    _emailer = nparcel.Emailer()

    def __init__(self,
                 report,
                 pidfile,
                 dry=False,
                 batch=True,
                 config=None):
        nparcel.DaemonService.__init__(self,
                                       pidfile=pidfile,
                                       dry=dry,
                                       batch=batch)

        self.set_report_type(report)

        if config is not None:
            self.set_config(nparcel.ReporterB2CConfig(file=config,
                                                      type=self.report_type))
            self.config.parse_config()

        log_msg = self.facility + '.%s not set via config: %s. Using "%s"'
        try:
            if self.config.report_outfile is not None:
                self.set_outfile(self.config.report_outfile)
        except AttributeError, err:
            log.debug(log_msg % ('outfile', err, self.outfile))

        try:
            if self.config.report_outfile_ts_format is not None:
                tmp_ts_format = self.config.report_outfile_ts_format
                self.set_outfile_ts_format(tmp_ts_format)
        except AttributeError, err:
            log.debug(log_msg % ('outfile_ts_format', err, self.outfile))

        try:
            if self.config.report_outdir is not None:
                self.set_outdir(self.config.report_outdir)
        except AttributeError, err:
            log.debug(log_msg % ('outdir', err, self.outdir))

        try:
            if self.config.report_extension is not None:
                self.set_extension(self.config.report_extension)
        except AttributeError, err:
            log.debug(log_msg % ('report_extension', err, self.extension))

        # Generic report overrides.
        log_msg = self.facility + '.%s not set via config: %s. Using "%s"'
        try:
            getter = getattr(self.config, 'report_type_outfile')
            if getter is not None:
                self.set_outfile(getter)
        except AttributeError, err:
            log.debug(log_msg % ('outfile', err, self.outfile))

        try:
            getter = getattr(self.config, 'report_type_display_hdrs')
            if getter is not None:
                self.set_display_hdrs(getter)
        except AttributeError, err:
            log.debug(log_msg % ('display_hdrs', err, self.display_hdrs))

        try:
            getter = getattr(self.config, 'report_type_aliases')
            if getter is not None:
                self.set_aliases(getter)
        except AttributeError, err:
            log.debug(log_msg % ('report_type_aliases',
                                 err,
                                 self.aliases))

        try:
            getter = getattr(self.config, 'report_type_widths')
            if getter is not None:
                self.set_header_widths(getter)
        except AttributeError, err:
            log.debug(log_msg % ('header_widths',
                                 err,
                                 self.header_widths))

        try:
            getter = getattr(self.config, 'report_type_ws')
            if getter is not None:
                self.set_ws(getter)
        except AttributeError, err:
            log.debug(log_msg % ('ws', err, self.ws))

        try:
            getter = getattr(self.config, 'report_type_recipients')
            if getter is not None:
                self.set_recipients(getter)
        except AttributeError, err:
            log.debug(log_msg % ('recipients', err, self.recipients))

        try:
            getter = getattr(self.config, 'report_type_bu_based')
            if getter is not None:
                self.set_bu_based(getter)
        except AttributeError, err:
            log.debug(log_msg % ('bu_based', err, self.bu_based))

        try:
            getter = getattr(self.config, 'report_type_delivery_partners')
            if getter is not None:
                self.set_delivery_partners(getter)
        except AttributeError, err:
            log.debug(log_msg % ('delivery_partners',
                                 err,
                                 self.delivery_partners))

        try:
            if self.config.report_bu_id_recipients.keys() > 0:
                tmp_bu_ids = self.config.report_bu_id_recipients
                self.set_bu_id_recipients(tmp_bu_ids)
        except AttributeError, err:
            log.debug(log_msg % ('bu_id_recipients',
                                 err,
                                 self.bu_id_recipients))

        try:
            if self.config.report_compliance_period is not None:
                tmp_period = self.config.report_compliance_period
                self.set_compliance_period(tmp_period)
        except AttributeError, err:
            log.debug(log_msg % ('report_compliance_period',
                                 err,
                                 self.compliance_period))

    @property
    def report_type(self):
        return self._report_type

    def set_report_type(self, value):
        self._report_type = value
        log.debug('%s report_type set to "%s"' %
                  (self.facility, self.report_type))

    @property
    def config(self):
        return self._config

    def set_config(self, value):
        self._config = value

    @property
    def bu_ids(self):
        return self._bu_ids

    def set_bu_ids(self, values):
        self._bu_ids.clear()

        if values is not None:
            self._bu_ids = values
        log.debug('%s.bu_ids set to "%s"' % (self.facility, self._bu_ids))

    @property
    def outdir(self):
        return self._outdir

    def set_outdir(self, value):
        self._outdir = value
        create_dir(self.outdir)
        log.debug('%s.outdir set to "%s"' % (self.facility, self.outdir))

    @property
    def outfile(self):
        return self._outfile

    def set_outfile(self, value):
        self._outfile = value
        log.debug('%s.outfile set to "%s"' % (self.facility, self.outfile))

    @property
    def outfile_ts_format(self):
        return self._outfile_ts_format

    def set_outfile_ts_format(self, value):
        self._outfile_ts_format = value
        log.debug('%s.outfile_ts_format set to "%s"' %
                  (self.facility, self.outfile_ts_format))

    @property
    def extension(self):
        return self._extension

    def set_extension(self, value):
        self._extension = value
        log.debug('%s.extension set to "%s"' %
                  (self.facility, self.extension))

    @property
    def display_hdrs(self):
        return self._display_hdrs

    def set_display_hdrs(self, values=None):
        del self._display_hdrs[:]
        self._display_hdrs

        if values is not None:
            self._display_hdrs.extend(values)
        log.debug('%s.display_hdrs set to "%s"' %
                  (self.facility, self.display_hdrs))

    @property
    def aliases(self):
        return self._aliases

    def set_aliases(self, values=None):
        self._aliases.clear()

        if values is not None:
            self._aliases = values
        log.debug('%s.aliases set to "%s"' % (self.facility, self._aliases))

    @property
    def header_widths(self):
        return self._header_widths

    def set_header_widths(self, values=None):
        self._header_widths.clear()

        if values is not None:
            self._header_widths = values
        log.debug('%s.header_widths set to "%s"' %
                  (self.facility, self._header_widths))

    @property
    def ws(self):
        return self._ws

    def set_ws(self, values=None):
        self._ws.clear()

        if values is not None:
            self._ws = values
        else:
            self._ws = {'title': str(),
                        'sub_title': str(),
                        'sheet_title': str()}
        log.debug('%s.ws set to "%s"' % (self.facility, self._ws))

    @property
    def report_filename(self):
        return self._report_filename

    def set_report_filename(self, value):
        self._report_filename = value
        log.debug('%s.report_filename set to "%s"' %
                  (self.facility, self._report_filename))

    @property
    def recipients(self):
        return self._recipients

    def set_recipients(self, values=None):
        del self._recipients[:]
        self._recipients

        if values is not None:
            self._recipients.extend(values)
        log.debug('%s.recipients set to "%s"' %
                  (self.facility, self._recipients))

    @property
    def bu_id_recipients(self):
        return self._bu_id_recipients

    def set_bu_id_recipients(self, values):
        self._bu_id_recipients.clear()

        if values is not None:
            self._bu_id_recipients = values
        log.debug('%s.bu_id_recipients set to "%s"' %
                   (self.facility, self.bu_id_recipients))

    @property
    def delivery_partners(self):
        return self._delivery_partners

    def set_delivery_partners(self, values=None):
        del self._delivery_partners[:]
        self._delivery_partners

        if values is not None:
            self._delivery_partners.extend(values)
        log.debug('%s.delivery_partners set to "%s"' %
                    (self.facility, self._delivery_partners))

    @property
    def bu_based(self):
        return self._bu_based

    def set_bu_based(self, value):
        self._bu_based = (value == True)
        log.debug('%s.bu_based set to "%s"' % (self.facility, self.bu_based))

    @property
    def compliance_period(self):
        return self._compliance_period

    def set_compliance_period(self, value):
        self._compliance_period = value
        log.debug('%s.compliance_period set to %s (days)' %
                  (self.facility, self.compliance_period))

    @property
    def reporter_kwargs(self):
        kwargs = {}
        try:
            kwargs['db_kwargs'] = self.config.db_kwargs()
        except AttributeError, err:
            log.debug('%s db_kwargs not in config: %s ' %
                      (self.facility, err))

        if self.report_type in ['uncollected',
                                'noncompliance',
                                'totals',
                                'collected']:
            try:
                if self.config.report_bu_ids is not None:
                    self.set_bu_ids(self.config.report_bu_ids)
            except AttributeError, err:
                log.debug('%s bu_ids not in config: %s. Using "%s"' %
                          (self.facility, err, self.bu_ids))
            kwargs['bu_ids'] = self.bu_ids

        try:
            if self.config.report_type_delivery_parters is not None:
                self.set_bu_ids(self.config.report_type_delivery_partners)
        except AttributeError, err:
            msg = '%s %s not in config: %s. Using "%s"'
            log.debug(msg % (self.facility,
                             'report_type_delivery_partner',
                             err,
                             self.bu_ids))
        kwargs['delivery_partners'] = self.delivery_partners

        log.debug('%s.reporter_kwargs: "%s"' % (self.facility, kwargs))
        return kwargs

    def _start(self, event):
        """Override the :method:`nparcel.utils.Daemon._start` method.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        # Initialise our report objects.
        if self._report is None:
            kwargs = self.reporter_kwargs
            if self.report_type == 'uncollected':
                self._report = nparcel.Uncollected(**kwargs)
            elif self.report_type == 'compliance':
                self._report = nparcel.Compliance(**kwargs)
                self._report.set_period(self.compliance_period)
            elif self.report_type == 'noncompliance':
                self._report = nparcel.NonCompliance(**kwargs)
            elif self.report_type == 'exception':
                self._report = nparcel.Exception(**kwargs)
            elif self.report_type == 'totals':
                self._report = nparcel.Totals(**kwargs)
            elif self.report_type == 'collected':
                self._report = nparcel.Collected(**kwargs)

        # Set the report PROD instance name.
        try:
            self._report.set_prod(self.config.prod)
        except AttributeError, err:
            log.debug('%s prod instance name not in config: %s ' %
                      (self.facility, err))

        while not event.isSet():
            now = datetime.datetime.now().strftime(self.outfile_ts_format)

            if self._report is None:
                log.error('Reporter is not defined -- aborting')
                event.set()
                break

            if not self._bu_based:
                self.set_bu_id_recipients({None: []})
            for id in self.bu_id_recipients.keys():
                rows = self._report.process(id=id, dry=self.dry)

                # Write out the export file.
                file_bu_id = str(id)
                if not self.bu_based:
                    file_bu_id = 'all'
                outfile = '%s%s-%s.%s' % (self.outfile,
                                          now,
                                          file_bu_id,
                                          self.extension)
                if self.outdir is not None:
                    outfile = os.path.join(self.outdir, outfile)
                self.set_report_filename(outfile)
                writer = nparcel.Xlwriter(outfile)

                writer.set_title(self.ws.get('title'))
                writer.set_subtitle(self.ws.get('subtitle'))
                writer.set_worksheet_title(self.ws.get('sheet_title'))

                filtered_rows = []
                for row in rows:
                    filtered_row = writer.filter(self._report.columns,
                                                 self.display_hdrs,
                                                 row)
                    filtered_rows.append(filtered_row)
                aliased_hdrs = writer.header_aliases(self.display_hdrs,
                                                     self.aliases)
                writer.set_headers(aliased_hdrs)
                writer.set_header_widths(self.header_widths)
                writer(filtered_rows)

                if self.bu_based:
                    # Override the recipients
                    tmp_recipients = self.bu_id_recipients.get(id)
                    if tmp_recipients is None:
                        tmp_recipients = []
                    subject_bu = self.bu_ids.get(id)
                    self.set_recipients(tmp_recipients)
                    self.send_email(bu=subject_bu)
                else:
                    self.send_email(bu='all')
                    break

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()

    def send_email(self, date_ts=None, bu=None):
        """Send the report via email.

        **Kwargs:**
            *date_ts*: :mod:`datetime` object that can override the
            report date and time.

            *bu*: the Business Unit string description.  For example,
            ``Toll Priority``

        **Returns:**
            ``True`` for processing success

            ``False`` for processing failure

        """
        status = True

        title = self.ws.get('title')
        if date_ts is None:
            now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        else:
            now = date_ts.strftime('%d/%m/%Y')

        data = {'title': title,
                'bu': bu,
                'date': now}
        mime = self._emailer.create_comms(data=data,
                                          template='report',
                                          files=[self.report_filename],
                                          prod=self._report.prod)
        self._emailer.set_recipients(self.recipients)
        status = self._emailer.send(mime_message=mime, dry=self.dry)

        return status
