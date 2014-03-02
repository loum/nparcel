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
    _facility = None

    def __init__(self, config_file=None):
        """Nparcel Config initialisation.
        """
        self._facility = self.__class__.__name__

        ConfigParser.SafeConfigParser.__init__(self)

        self._config_file = config_file
        if self._config_file is not None:
            self.set_config_file(self._config_file)

    @property
    def facility(self):
        return self._facility

    @property
    def config_file(self):
        return self._config_file

    def set_config_file(self, value):
        """Set the configuration file to *value* and attempt to read
        the contents (unless *value* is ``None``).

        File contents should be as per :mod:`ConfigParser` format.

        **Args:**
            *value*: typically the path to the configuration file.

        """
        log.debug('Setting config file to "%s"' % value)
        self._config_file = value

        if self._config_file is not None:
            if os.path.exists(self._config_file):
                log.debug('Reading config file: "%s"' % self._config_file)
                self.read(self._config_file)
            else:
                log.critical('Unable to locate config file: "%s"' %
                             self._config_file)
                sys.exit(1)

    def parse_config(self):
        """Simple file checker for the base module.

        """
        if self.config_file is None:
            log.critical('Cannot parse config -- no file defined')
            sys.exit(1)
