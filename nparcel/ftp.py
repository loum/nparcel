__all__ = [
    "Ftp",
]
import os
import sys
import ftplib
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
