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

    """
    _file = None
    _in_dirs = []
    _dry = False
    _batch = False
    _emailer = nparcel.Emailer()
    _reporter = nparcel.Reporter()
    _loop = 30
    _support_emails = []
    _archive_base = None

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False):
        super(DaemonService, self).__init__(pidfile=pidfile)

        self._file = file
        self._dry = dry
        self._batch = batch

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

        if values is not None:
            log.debug('Set inbound directory list "%s"' % str(values))
            self._in_dirs.extend(values)
        else:
            self._in_dirs = []

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
        self._loop = value

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
        log.debug('Set archive base directory to "%s"' % self._archive_base)

    def alert(self,
              template,
              data,
              subject_data=None,
              recipients=None,
              dry=False):
        """Use the :attr:`nparcel.Emailer` object to generate email
        notification based on *template* and *data* dictionary value.

        *subject_data* can be delivered in a few ways:
        * as a string it will simply pass it through to the subject email

        * as a dictionary in the form::

            {'data': {<key>: <value>,
                      ...},
             'template': <template>}

        where the ``data`` and ``template`` keys which define the
        template arrangment

        * nothing at all (``None``) in which case it will try to fudge
        a subject template based on the email body template

        **Args:**
            *template*: the email template to use to generate the HTML-based
            email content.  Template format is ``email_<name>_html.t`` where
            ``<name>`` is the expected argument value

            *data*: dictionary structure that contains the values that will
            plug into the template file

        **Kwargs:**
            *subject_data*: string or dictionary value that will form
            the email subject line

            *recipients*: list of email addresses to send to.  If not
            ``None``, will override the :attr:`nparcel.Emailer.recipients`
            values

            *dry*: don't execute, just report

        """
        if recipients is not None:
            self.emailer.set_recipients(recipients)

        subject = str()
        subject_template_data = {}
        subject_template = None
        if subject_data is not None:
            if isinstance(subject_data, str):
                subject = subject_data
            elif isinstance(subject_data, dict):
                subject_template_data = subject.get('data')
                subject_template = subject.get('template')

        if not subject and subject_template is None:
            subject = self.emailer.get_subject_line(data,
                                                    template=template)
            subject = subject.rstrip()

        mime = self.emailer.create_comms(subject=subject,
                                         data=data,
                                         template=template)
        self.emailer.send(mime_message=mime, dry=dry)

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
