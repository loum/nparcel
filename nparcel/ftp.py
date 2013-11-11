__all__ = [
    "Ftp",
]
import os
import sys
import ftplib
import socket

import nparcel
import ConfigParser
from nparcel.utils.log import log
from nparcel.utils.files import (create_dir,
                                 get_directory_files)


class Ftp(ftplib.FTP):
    """Nparcel FTP client.

    .. attribute:: archive_dir

        where to archive signature files (if not being transfered).
        Default of ``None`` will not archive files.

    .. attribute:: config

        :mod:`nparcel.Config` object

    .. attribute:: xfer

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
        host = self.config.get(xfer, 'host')
        port = self.config.get(xfer, 'port')
        user = self.config.get(xfer, 'user')
        password = self.config.get(xfer, 'password')
        target = self.config.get(xfer, 'target')

        try:
            log.info('Connecting to "%s:%s"' % (host, port))
            self.connect(host=host, port=port)
        except socket.error, err:
            log.critical('Connection failed: %s' % err)
            sys.exit(1)

        try:
            log.info('Login as "%s"' % user)
            self.login(user=user, passwd=password)
        except ftplib.error_perm, err:
            log.critical('Login failed: %s' % err)
            sys.exit(1)

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

        log.info('Closing FTP session to "%s"' % host)
        self.quit()

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
