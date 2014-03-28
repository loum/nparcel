__all__ = [
    "DaemonService",
]
import nparcel
from nparcel.utils.log import log


class DaemonService(nparcel.utils.Daemon):
    """Common components for the Daemoniser facility.

    .. attribute:: file

        daemonisers can handle a single iteration if a file is provided

    .. attribute:: in_dirs

        list of directories to search for inbound files to process

    .. attribute:: dry

        don't actually run, just report

    .. attribute:: batch

        single iteration

    .. attribute:: emailer

        :mod:`nparcel.Emailer` object

    .. attribute:: reporter

        :mod:`nparcel.Reporter` object

    .. attribute:: loop

        integer value that represents the sleep period between
        processing iterations (default 30 seconds)

    .. attribute:: support_emails

        list of support emails address

    .. attribute:: archive_base

        base directory where processed files are archived

    .. attribute:: prod

        hostname of the production instance

    """
    _facility = None
    _file = None
    _in_dirs = []
    _dry = False
    _batch = False
    _emailer = nparcel.Emailer()
    _reporter = nparcel.Reporter()
    _loop = 30
    _support_emails = []
    _archive_base = None
    _prod = None

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False):
        self._facility = self.__class__.__name__

        nparcel.utils.Daemon.__init__(self, pidfile=pidfile)

        self._file = file
        self._dry = dry
        self._batch = batch

    @property
    def facility(self):
        return self._facility

    @property
    def file(self):
        return self._file

    def set_file(self, value=None):
        self._file = value

    @property
    def in_dirs(self):
        return self._in_dirs

    def set_in_dirs(self, values):
        del self._in_dirs[:]
        self._in_dirs = []

        if values is not None:
            self._in_dirs.extend(values)
        log.debug('%s in_dirs set to "%s"' % (self.facility, self.in_dirs))

    @property
    def dry(self):
        return self._dry

    def set_dry(self, value=True):
        self._dry = value

    @property
    def batch(self):
        return self._batch

    def set_batch(self, value=True):
        self._batch = value

    @property
    def emailer(self):
        return self._emailer

    @property
    def reporter(self):
        return self._reporter

    @property
    def loop(self):
        return self._loop

    def set_loop(self, value):
        self._loop = int(value)
        log.debug('%s loop set to %d' % (self.facility, self.loop))

    @property
    def support_emails(self):
        return self._support_emails

    def set_support_emails(self, values=None):
        del self._support_emails[:]
        self._support_emails = []

        if values is not None and isinstance(values, list):
            self._support_emails.extend(values)

    @property
    def archive_base(self):
        return self._archive_base

    def set_archive_base(self, value):
        self._archive_base = value
        log.debug('%s archive_base set to "%s"' %
                  (self.facility, self._archive_base))

    @property
    def prod(self):
        return self._prod

    def set_prod(self, value=None):
        self._prod = value.lower()
        log.debug('%s prod instance name set to "%s"' %
                  (self.facility, self.prod))

    def create_table(self, items):
        """Takes a list of *items* and generates string based, variable
        table content that can feed into a static string template.

        **Args:**
            *items*: list of items to present in the table

        **Returns:**
            string-based HTML table construct

        """
        table_str = []
        tr = '<tr style="border:1px solid white">'
        td = '<td style="white-space:nowrap">'

        for i in items:
            td_str = ('%s\n    %s\n        %s\n    %s\n%s' %
                      (tr, td, i, '</td>', '</tr>'))
            table_str.append(td_str)

        return "\n".join(table_str)

    def send_table(self,
                   recipients,
                   table_data,
                   files=None,
                   template='proc_err',
                   dry=False):
        """Send an table-structured email message based on the list
        *table_data*.

        Acts as a wrapper that will create the MIME message including
        a list of *files* to attach and send to the list of *recipients*.

        E-mail is sent via the SMTP gateway.

        E-mail message is based on the *template*..

        **Args:**
            *recipients*: list of email addresses to send e-mail to

            *messages*: list of messages to be sent.  List will be
            converted into a HTML table

        **Kwargs:**
            *files*: list of files to send as an attachment

            *dry*: do not send, only report what would happen

        **Returns:**

            ``True`` for successful email send

            ``False`` otherwise

        """
        log.debug('Received table_data list: "%s"' % table_data)
        status = False

        if len(table_data):
            alert_table = self.create_table(table_data)
            data = {'file': file,
                    'facility': self.facility,
                    'err_table': alert_table}
            mime = self.emailer.create_comms(data=data,
                                             template=template,
                                             files=files,
                                             prod=self.prod)
            self.emailer.set_recipients(recipients)
            status = self.emailer.send(mime_message=mime, dry=dry)

        else:
            log.debug('No table data generated -- suppressing comms')

        return status
