__all__ = [
    "DaemonService",
]
import top
from top.utils.log import log
from top.utils.files import (get_directory_files,
                             check_filename)
from top.utils.setter import (set_scalar,
                              set_list)


class DaemonService(top.utils.Daemon):
    """Common components for the Daemoniser facility.
    .. attribute:: config

        an :class:`top.B2CConfig` type object

    .. attribute:: file

        daemonisers can handle a single iteration if a file is provided

    .. attribute:: in_dirs

        list of directories to search for inbound files to process

    .. attribute:: dry

        don't actually run, just report

    .. attribute:: batch

        single iteration

    .. attribute:: emailer

        :mod:`top.Emailer` object

    .. attribute:: reporter

        :mod:`top.Reporter` object

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
    _prod = None
    _support_emails = []
    _config = None
    _facility = None
    _file = None
    _in_dirs = []
    _dry = False
    _batch = False
    _emailer = top.Emailer()
    _reporter = top.Reporter()
    _loop = 30
    _archive_base = None

    @property
    def prod(self):
        return self._prod

    @set_scalar
    def set_prod(self, value=None):
        pass

    @property
    def support_emails(self):
        return self._support_emails

    @set_list
    def set_support_emails(self, values=None):
        pass

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config=None):
        top.utils.Daemon.__init__(self, pidfile=pidfile)

        if config is not None:
            self._config = config

            # Grab the base configuration items required by all daemons.
            prod = self.config.parse_scalar_config('environment', 'prod')
            support = self.config.parse_scalar_config('email',
                                                      'support',
                                                      var='support_emails',
                                                      is_list=True)
            # Now, parse the daemon-specific config items.
            self.config.parse_config()
            if prod is not None:
                self.set_prod(prod.lower())
            self.set_support_emails(support)

        self._facility = self.__class__.__name__

        self._file = file
        self._dry = dry
        self._batch = batch

    @property
    def config(self):
        return self._config

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

    @set_list
    def set_in_dirs(self, values=None):
        pass

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

    @set_scalar
    def set_loop(self, value):
        pass

    @property
    def archive_base(self):
        return self._archive_base

    def set_archive_base(self, value):
        self._archive_base = value
        log.debug('%s archive_base set to "%s"' %
                  (self.facility, self._archive_base))

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
                   identifier=None,
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
            *identifier*: identifying token that will be displayed in the
            message.  For example, :mod:`top.LoaderDaemon` processing
            errors are usually identified by the T1250 EDI file that
            caused the error

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
                    'identifier': identifier,
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

    def get_files(self, dir=None, formats=None):
        """Identifies files that are to be processed.

        **Args:**
            *dir*: override :attr:`in_dirs` for directories to search

            *formats*: list of regular expressions to apply across
            directory files

        **Returns:**
            list of files found

        """
        if formats is None:
            formats = []

        files_to_process = []

        dirs_to_check = self.in_dirs
        if dir is not None:
            dirs_to_check = dir

        for dir_to_check in dirs_to_check:
            log.debug('Looking for files at: %s ...' % dir_to_check)
            for file in get_directory_files(dir_to_check):
                for format in formats:
                    if (check_filename(file, format)):
                        log.info('Found file: %s' % file)
                        files_to_process.append(file)

        files_to_process.sort()
        log.debug('Files set to be processed: "%s"' % str(files_to_process))

        return files_to_process
