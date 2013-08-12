__all__ = [
    "Ftp",
]
import os
import sys
import ftplib
import fnmatch
import ConfigParser

from nparcel.utils.log import log


class Ftp(ftplib.FTP):
    """Nparcel FTP client.
    """

    def __init__(self,
                 config_file='npftp.conf'):
        """Nparcel Ftp initialisation.
        """
        ftplib.FTP.__init__(self)

        self._config = ConfigParser.SafeConfigParser()
        self._xfers = []

        self.set_config_file(config_file)

    @property
    def config(self):
        return self._config

    @property
    def xfers(self):
        return self._xfers

    @property
    def config_file(self):
        return self._config_file

    def set_config_file(self, value):
        self._config_file = value

        if self._config_file is not None:
            if os.path.exists(self._config_file):
                log.info('Parsing config file: "%s"' % self._config_file)
                self._config.read(self._config_file)
            else:
                log.critical('Unable to locate config file: "%s"' %
                             self._config_file)
                sys.exit(1)

    def _parse_config(self):
        """Read config items from the configuration file.

        Each section that starts with ``ftp_`` are interpreted as an FTP
        connection to process.

        """
        if self.config_file is None:
            log.critical('Cannot parse config -- no file defined')
            sys.exit(1)

        # Parse each section.
        for section in self._config.sections():
            if section[:4] == 'ftp_':
                self._xfers.append(section)

    def get_report_file(self, dir):
        """Identifies report files in directory *dir*.

        **Args:**
            dir: the directory to search for report files.

        **Returns:**
            list of report files
        """
        log.info('Looking for report files in directory: "%s"' % dir)
        for file in os.listdir(dir):
            file = os.path.join(dir, file)
            if os.path.isfile(file):
                if fnmatch.fnmatch(os.path.basename(file),
                                   'VIC_VANA_RE*.txt'):
                    log.info('Found report file: "%s"' % file)
                    yield file

    def get_report_file_ids(self, file):
        """Parse report file and extract a list of JOB_KEY's

        **Args:**
            file: fully qualified name to the report file

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
        """
        """
        self._parse_config()
        for xfer in self.xfers:
            files_to_xfer = []

            log.info('Processing transfers for "%s"' % xfer)
            source = self.config.get(xfer, 'source')
            log.debug('Sourcing files from local directory: "%s"' % source)

            keys = []
            for report in self.get_report_file(source):
                keys = self.get_report_file_ids(report)

                for key in keys:
                    sig_file = os.path.join(source, '%s.ps' % key)
                    files_to_xfer.append(sig_file)

                # ... and append the report file.
                files_to_xfer.append(report)

            if files_to_xfer:
                self.xfer_files(xfer, files_to_xfer)

    def xfer_files(self, xfer, files):
        """
        """
        host = self.config.get(xfer, 'host')
        port = self.config.get(xfer, 'port')
        user = self.config.get(xfer, 'user')
        password = self.config.get(xfer, 'password')
        target = self.config.get(xfer, 'target')

        self.connect(host=host, port=port)
        self.login(user=user, passwd=password)

        for file in files:
            log.info('Transferring "%s"' % file)

        self.quit()
