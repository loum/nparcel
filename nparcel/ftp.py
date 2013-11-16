__all__ = [
    "Ftp",
]
import os
import ftplib
import socket

import nparcel
import ConfigParser
from nparcel.utils.log import log
from nparcel.utils.files import (create_dir,
                                 check_filename,
                                 get_directory_files)


class Ftp(ftplib.FTP):
    """Nparcel FTP client.

    .. attribute:: archive_dir

        where to archive signature files (if not being transfered).
        Default of ``None`` will not archive files.

    .. attribute:: config

        :mod:`nparcel.Config` object

    .. attribute:: xfers

        list of FTP instances that define an FTP context.  For example,
        consider this typical FTP configuration definition::

            [ftp_priority]
            host = localhost
            port = 21
            user = priority
            password = prior_pw
            source = /data/nparcel/priority/out
            target = in

        This ``ftp_priority`` section definition will be appended to the
        :attr:`xfer` list

    """
    _archive_dir = '/data/nparcel/archive/ftp'
    _config = nparcel.Config()
    _xfers = []

    def __init__(self, config_file=None):
        """Nparcel Ftp initialisation.

        """
        ftplib.FTP.__init__(self)

        if config_file is not None:
            self._config.set_config_file(config_file)
            self._parse_config()

    @property
    def config(self):
        return self._config

    @property
    def xfers(self):
        return self._xfers

    @property
    def archive_dir(self):
        return self._archive_dir

    def reset_config(self):
        del self._xfers[:]
        self._xfers = []

        self._config = nparcel.Config()

    def set_archive_dir(self, value):
        self._archive_dir = value

        if self._archive_dir is not None:
            if not create_dir(self._archive_dir):
                self._archive_dir = None

    def _parse_config(self, file_based=True):
        """Read config items from the configuration source.

        Each section that starts with ``ftp_`` are interpreted as an FTP
        connection to process.

        **Kwargs:**
            *file_based*: boolean value that define whether the
            configuration source is file based or not

        """
        if file_based:
            self.config.parse_config()

        # Parse each section.
        for section in self.config.sections():
            if section[:4] == 'ftp_':
                self.xfers.append(section)

        try:
            self.set_archive_dir(self.config.get('dirs', 'archive'))
            log.debug('FTP archive directory: %s' % self.archive_dir)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            log.info('Archive directory not in config - using to "%s"' %
                     self.archive_dir)

    def get_report_file(self, dir, file_filter=None):
        """Identifies report files in directory *dir* based on file
        filtering rule provided by *file_filter*.

        **Args:**
            *dir*: the directory to search for report files.

        **Kwargs:**
            *file_filter*: regular expression format to limit file listing
            Defaults to ``None`` which will return all files in the
            directory

        **Returns:**
            list of report files

        """
        log.info('Sourcing files from local directory: "%s"' % dir)
        return get_directory_files(path=dir, filter=file_filter)

    def get_report_file_ids(self, file):
        """Parse report file and extract a list of JOB_KEY's

        **Args:**
            *file*: fully qualified name to the report file

        **Returns:**
            list of JOB_KEY values

        """
        log.info('Checking file "%s" for JOB_KEYs' % file)
        keys = []

        try:
            fh = open(file)
            # Consume the header.
            fh.readline()
            for line in fh:
                keys.append(line.rsplit('|')[1])
        except IOError, err:
            log.error('Could not open file "%s"' % file)

        return keys

    def process(self, dry=False):
        """Transfer signature files and reports.

        Cycles through each transfer context and prepares a list of files
        that will be transferred.

        **Kwargs:**
            *dry*: only report, do not execute

        """
        for xfer in self.xfers:
            log.info('Processing transfers for "%s"' % xfer)

            try:
                direction = self.config.get(xfer, 'direction')
                direction = direction.lower()
            except ConfigParser.NoOptionError, err:
                direction = 'outbound'

            if direction == 'outbound':
                self.outbound(xfer, dry=dry)

    def inbound(self, xfer, dry=False):
        """Incoming file transfer.

        **Args:**
            *xfer*: a :mod:`ConfigParser` section that represents
            an FTP transfer instance

        """
        log.info('Preparing outbound xfer ...')

        if self.connect_resource(xfer):
            xfer_set = []
            try:
                source = self.config.get(xfer, 'source')
            except ConfigParser.NoOptionError:
                source = None

            if source is not None:
                log.info('Setting CWD on server to "%s"' % source)
                self.cwd(source)

            log.debug('Getting remote listing ...')
            remote_files = self.nlst()
            try:
                source = self.config.get(xfer, 'source')
            except ConfigParser.NoOptionError:
                source = None

    def outbound(self, xfer, dry=False):
        """Outgoing file transfer.

        **Args:**
            *xfer*: a :mod:`ConfigParser` section that represents
            an FTP transfer instance

        **Kwargs:**
            *dry*: only report, do not execute

        """
        log.info('Preparing outbound xfer ...')

        if self.connect_resource(xfer):
            xfer_set = []
            source = self.config.get(xfer, 'source')

            try:
                filter = self.config.get(xfer, 'filter')
            except ConfigParser.NoOptionError, err:
                filter = None

            try:
                is_pod = (self.config.get(xfer, 'pod') == 'True')
            except ConfigParser.NoOptionError, err:
                is_pod = False

            xfer_set = self.get_xfer_files(source, filter, is_pod)

            if len(xfer_set):
                self.xfer_files(xfer, xfer_set, dry=dry)

            self.disconnect_resource()

    def get_xfer_files(self, source, filter=None, is_pod=False):
        """For outbound file transfers, get a list of files to transfer.

        **Args:**
            *source*: directory path where outbound files can be found

        **Kwargs:**
            *filter*: regular expression string to use to filter filenames

            *is_pod*: POD file require extra processing to identify
            associated signature files.

        """
        files_to_xfer = []

        for report in self.get_report_file(source, filter):
            if is_pod:
                for key in self.get_report_file_ids(report):
                    for ext in ['ps', 'png']:
                        pod = os.path.join(source, '%s.%s' % (key, ext))
                        files_to_xfer.append(pod)

            files_to_xfer.append(report)

        return files_to_xfer

    def xfer_files(self, xfer, files, dry=False):
        """Transfer files defined by *files* list.

        Archives the transfered file upon success.

        **Args:**
            *xfer*: the config section of the current FTP context.

            *files*: list of files to transfer

        """
        try:
            target = self.config.get(xfer, 'target')
        except ConfigParser.NoOptionError:
            target = None

        if target is not None:
            log.info('Setting CWD on server to "%s"' % target)
            self.cwd(target)

        for file in files:
            if os.path.exists(file):
                filename = os.path.basename(file)
                f = open(file, 'rb')
                log.info('Transferring "%s" to "%s" ...' % (file, filename))
                if not dry:
                    self.storbinary('STOR %s' % filename, f)
                log.info('Transfer "%s" OK' % file)
                f.close()

                self.archive_file(file, dry=dry)

    def get_files(self, files, target_dir=None, partial=False, dry=False):
        """Retrives files defined by *files* list.

        Archives the transfered file upon success.

        **Args:**
            *xfer*: the config section of the current FTP context.

            *files*: list of files to transfer

        **Kwargs:**
            *partial*: as transfers are incremental, boolean ``True``
            will append ``.tmp`` to the filename on the local file
            directory resource (default is ``False``)

        **Returns:**
            list of filenames successfully transferred (as identified on
            the remote server)

        """
        log.info('Retrieving files ...')
        files_retrieved = []

        for f in files:
            log.info('Retrieving file "%s"' % f)
            target_file = f
            if target_dir is not None:
                target_file = os.path.join(target_dir, target_file)

            if partial:
                target_file = target_file + '.tmp'
                log.debug('Partial FTP local filename: "%s"' % target_file)

            if not dry:
                log.info('Retrieving file "%s" to "%s"' % (f, target_file))
                try:
                    fh = open(target_file, 'wb')
                    self.retrbinary('RETR %s' % f, fh.write)
                    fh.close()
                    files_retrieved.append(f)
                except IOError, e:
                    log.error('FTP retrieve error: e' % e)

        log.info('Retrieved files count: %d' % len(files_retrieved))

        return files_retrieved

    def archive_file(self, file, dry=False):
        """Move the Nparcel signature file and report to the archive
        directory.

        .. note::

            Move will only occur if archive directory is defined and exists.

        **Args:**
            *file*: full path of file to archive

        **Kwargs:**
            *dry*: only report what would happen (do not move file)

        **Returns:**
            ``boolean``::

                boolean ``True`` if file is archived successfully
                boolean ``False`` otherwise

        """
        status = True

        if self.archive_dir is None:
            log.info('Archive directory is not defined')
            status = False

        if status:
            target = os.path.join(self.archive_dir, os.path.basename(file))

            log.info('Archiving "%s" to "%s"' % (file, target))
            try:
                if not dry:
                    os.rename(file, target)
            except OSError, err:
                log.error('Signature file move failed: "%s"' % err)
                status = False

        return status

    def connect_resource(self, xfer):
        """ Connect to the FTP resource.

        """
        host = self.config.get(xfer, 'host')
        port = self.config.get(xfer, 'port')
        user = self.config.get(xfer, 'user')
        password = self.config.get(xfer, 'password')

        try:
            proxy = self.config.get(xfer, 'proxy')
        except ConfigParser.NoOptionError:
            proxy = None

        status = True
        try:
            if proxy is None:
                log.info('Connecting to "%s:%s"' % (host, port))
                self.connect(host=host, port=port)
            else:
                log.info('Connecting to proxy "%s"' % proxy)
                self.connect(host=proxy)
        except socket.error, err:
            log.error('Connection failed: %s' % err)
            status = False

        try:
            if proxy is None:
                log.info('Login as user "%s"' % user)
                self.login(user=user, passwd=password)
            else:
                proxy_user = '%s@%s' % (user, host)
                log.info('Login as proxy user "%s"' % proxy_user)
                self.login(user=proxy_user, passwd=password)
        except ftplib.error_perm, err:
            log.error('Login failed: %s' % err)
            status = False

        return status

    def disconnect_resource(self):
        """Disconnect from FTP session.

        """
        log.info('Closing FTP session')
        try:
            self.quit()
        except AttributeError, err:
            log.error('FTP close error: %s' % err)

    def filter_file_list(self, files, format):
        """Filters list of *files* based on the *filter* regular expression
        string.

        *Args*:
            *files*: list of filenames to check.  *format* will only
            be made against the files basename component

            *format*: the :mod:`re` format string to match against

        """
        log.info('Filtering remote file list against "%s"' % format)

        filtered_files = []
        for f in files:
            if check_filename(f, format):
                filtered_files.append(f)

        return filtered_files
