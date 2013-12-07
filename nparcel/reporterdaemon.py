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

    .. attribute::
        *bu_ids*: dictionary mapping between Business Unit ID (``job.bu_id``
        column) and a human-readable format.  The default is::

            {1: 'Toll Priority',
             2: 'Toll Fast',
             3: 'Toll IPEC'}

    .. attribute::
        *outfile*: output filename base

    .. attribute::
        *outfile_ts_format*: timestamp format to append to the *outfile*
        (default ``YYYYMMDDHHMMSS``)

    .. attribute::
        *outdir*: temporary working directory to where report files are
        staged to for further processing

    .. attribute::
        *extension*: report filename extension

    .. attribute:: db_kwargs

        dictionary of connection string values for the Toll Parcel Point
        database.  Typical format is::

            {'driver': ...,
             'host': ...,
             'database': ...,
             'user': ...,
             'password': ...,
             'port': ...}

    .. attribute::
        *display_hdrs*: list of column headers to display in the report
        This can control the order and appearance of the raw query column
        set

    .. attribute::
        *aliases*: dictionary of raw header names and the preferred alias
        to display in the report.  For example::

            {'DP_CODE': 'Agent',
             'AGENT_NAME': 'Agent Name',
             'JOB_BU_ID': 'Business Unit',
             'CONNOTE_NBR': 'Connote',
             'ITEM_NBR': 'Item Nbr',
             'PIECES': 'Pieces'}

    .. attribute::
        *header_widths*: dictionary of aliased header names and prefered
        column width.  For example::

                {'Agent Name': 30,
                 'Connote': 40,
                 'Item Nbr': 50,
                 'To': 30}

    .. attribute::
        *ws*: dictionary of values to represent within the Excel worksheet.
        Notable values include::

            {'title': ...
             'subtitle': ...
             'sheet_title': ...}

    .. attribute::
        *report_filename*: the generated report filename

    .. attribute::
        *recipients*: list of email recipients

    """
    _bu_ids = {1: 'Toll Priority',
               2: 'Toll Fast',
               3: 'Toll IPEC'}
    _outdir = '/data/nparcel/reports'
    _outfile = 'Stocktake_uncollected_aged_report_'
    _outfile_ts_format = '%Y%m%d%H%M%S'
    _extension = 'xlsx'
    _db_kwargs = None
    _display_hdrs = []
    _aliases = {}
    _header_widths = {}
    _ws = {}
    _report_filename = None
    _recipients = []

    def __init__(self,
                 pidfile,
                 dry=False,
                 batch=True,
                 config=None):
        super(ReporterDaemon, self).__init__(pidfile=pidfile,
                                             dry=dry,
                                             batch=batch)

        if config is not None:
            self.config = nparcel.B2CConfig(file=config)
            self.config.parse_config()

        try:
            if self.config.db_kwargs() is not None:
                self.set_db_kwargs(self.config.db_kwargs())
        except AttributeError, err:
            msg = ('DB kwargs not defined in config')
            log.info(msg)

        # TODO -- read outdir from the config.
        create_dir(self.outdir)
        self._report = nparcel.Uncollected(db_kwargs=self.db_kwargs,
                                           bu_ids=self.bu_ids)
        self._emailer = nparcel.Emailer()

    @property
    def bu_ids(self):
        return self._bu_ids

    def set_bu_ids(self, values):
        self._bu_ids.clear()

        if values is not None:
            self._bu_ids = values
            log.debug('Set bu_ids to "%s"' % self._bu_ids)
        else:
            log.debug('Cleared bu_ids')

    @property
    def outdir(self):
        return self._outdir

    def set_outdir(self, value):
        self._outdir = value
        log.debug('Set outbound directory to "%s"' % self._outdir)
        create_dir(self._outdir)

    @property
    def outfile(self):
        return self._outfile

    def set_outfile(self, value):
        log.debug('Setting outfile base to "%s"' % value)
        self._outfile = value

    @property
    def outfile_ts_format(self):
        return self._outfile_ts_format

    def set_outfile_ts_format(self, value):
        log.debug('Setting outfile time stamp format to "%s"' % value)
        self._outfile_ts_format = value

    @property
    def extension(self):
        return self._extension

    def set_extension(self, value):
        log.debug('Setting extension base to "%s"' % value)
        self._extension = value

    @property
    def db_kwargs(self):
        return self._db_kwargs

    def set_db_kwargs(self, value):
        if value is not None:
            self._db_kwargs = value

    @property
    def display_hdrs(self):
        return self._display_hdrs

    def set_display_hdrs(self, values=None):
        del self._display_hdrs[:]
        self._display_hdrs

        if values is not None:
            self._display_hdrs.extend(values)
            log.debug('Setting headers to display to "%s"' %
                      self._display_hdrs)
        else:
            log.debug('Clearing headers to display list')

    @property
    def aliases(self):
        return self._aliases

    def set_aliases(self, values=None):
        self._aliases.clear()

        if values is not None:
            self._aliases = values
            log.debug('Set aliases to "%s"' % self._aliases)
        else:
            log.debug('Cleared header alias list')

    @property
    def header_widths(self):
        return self._header_widths

    def set_header_widths(self, values=None):
        self._header_widths.clear()

        if values is not None:
            self._header_widths = values
            log.debug('Set header widths to "%s"' % self._header_widths)
        else:
            log.debug('Cleared header widths list')

    @property
    def ws(self):
        return self._ws

    def set_ws(self, values=None):
        self._ws.clear()

        if values is not None:
            self._ws = values
            log.debug('Set worksheet values to "%s"' % self._ws)
        else:
            log.debug('Cleared worksheet values')

    @property
    def report_filename(self):
        return self._report_filename

    def set_report_filename(self, value):
        self._report_filename = value
        log.debug('Set report filename to "%s"' % self._report_filename)

    @property
    def recipients(self):
        return self._recipients

    def set_recipients(self, values=None):
        del self._recipients[:]
        self._recipients

        if values is not None:
            self._recipients.extend(values)
            log.debug('Setting report recipients to "%s"' %
                      self._recipients)
        else:
            log.debug('Clearing headers to display list')

    def _start(self, event):
        """Override the :method:`nparcel.utils.Daemon._start` method.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        while not event.isSet():
            log.info('Starting stocktake report ...')
            now = datetime.datetime.now().strftime(self.outfile_ts_format)

            rows = self._report.process()

            # Write out the export file.
            outfile = '%s%s.%s' % (self.outfile, now, self.extension)
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

            self.send_email()

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

        """
        title = self.ws.get('title')
        if date_ts is None:
            now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        else:
            now = date_ts.strftime('%d/%m/%Y')
        subject_data = {'title': title,
                        'bu': bu,
                        'date': now}
        subject = self._emailer.get_subject_line(data=subject_data,
                                                 template='report')
        subject = subject.rstrip()

        data = {'title': title,
                'date': now}
        self._emailer.send_comms(template='report',
                                 subject_data=subject,
                                 data=data,
                                 recipients=self.recipients,
                                 files=[self.report_filename],
                                 dry=self.dry)
