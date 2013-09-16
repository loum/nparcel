__all__ = [
    "Config",
]
import os
import sys
import ConfigParser

from nparcel.utils.log import log


class Config(ConfigParser.SafeConfigParser):
    """Nparcel Config class.

    .. attribute:: *config_file*

        path to the configuration file to parse

    """

    def __init__(self, config_file=None):
        """Nparcel Config initialisation.
        """
        ConfigParser.SafeConfigParser.__init__(self)

        self._config_file = config_file

    @property
    def config_file(self):
        return self._config_file

    def set_config_file(self, value):
        self._config_file = value

        if self._config_file is not None:
            if os.path.exists(self._config_file):
                log.info('Reading config file: "%s"' % self._config_file)
                self.read(self._config_file)
            else:
                log.critical('Unable to locate config file: "%s"' %
                             self._config_file)
                sys.exit(1)

    def parse_config(self):
        """Read config items from the configuration file.

        Each section that starts with ``ftp_`` are interpreted as an FTP
        connection to process.

        """
        if self.config_file is None:
            log.critical('Cannot parse config -- no file defined')
            sys.exit(1)
