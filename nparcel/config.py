__all__ = [
    "Config",
]
import os
import sys
import ConfigParser

from nparcel.utils.log import log


class Config(object):
    """
    """

    def __init__(self, file=None):
        """
        """
        self._file = file
        self._config = ConfigParser.SafeConfigParser()

        self.dirs_to_check = []
        self.archive = None
        self.loader_loop = 30
        self.exporter_loop = 900

        if self._file is not None:
            self.set_file(self._file)
            self.parse_config()

    def __call__(self, item=None):
        if item is None:
            return self._config

        value = None
        if item == 'in_dirs':
            value = self.dirs_to_check
        elif item == 'archive_dir':
            value = self.archive
        elif item == 'loader_loop':
            value = self.loader_loop
        elif item == 'exporter_loop':
            value = self.exporter_loop

        return value

    def set_file(self, file):
        """
        """
        self._file = file

        if os.path.exists(self._file):
            log.info('Parsing config file: "%s"' % file)
            self._config.read(file)
        else:
            log.critical('Unable to locate config file: "%s"' % file)
            sys.exit(1)

    def parse_config(self):
        """Read config items from the configuration file.
        """
        # Required items (fail if otherwise).
        if self._file is None:
            log.critical('Cannot parse config -- no file defined')
            sys.exit(1)

        try:
            self.dirs_to_check = self._config.get('dirs', 'in').split(',')
            log.info('Directories to check %s' % str(self.dirs_to_check))
            self.archive = self._config.get('dirs', 'archive')
            log.info('Archive directory %s' % self.archive)
        except ConfigParser.NoOptionError, err:
            log.error('Missing required config: %s' % err)
            sys.exit(1)

        # Optional items (defaults provided).
        try:
            self.loader_loop = int(self._config.get('timeout',
                                                    'loader_loop'))
            self.exporter_loop = int(self._config.get('timeout',
                                                      'exporter_loop'))
        except ConfigParser.NoOptionError, err:
            log.warn('"Timeout section error: %s' % err)
            pass

    def db_kwargs(self):
        """
        """
        kwargs = None

        # Base assumptions on "host" keyword.
        # No "host" means this must be a test scenario.
        try:
            host = self._config.get('db', 'host')
            driver = self._config.get('db', 'driver')
            database = self._config.get('db', 'database')
            user = self._config.get('db', 'user')
            password = self._config.get('db', 'password')
            port = self._config.get('db', 'port')
            kwargs = {'driver': driver,
                      'host': host,
                      'database': database,
                      'user': user,
                      'password': password,
                      'port': int(port)}
        except ConfigParser.NoOptionError, err:
            log.error('Missing DB key via config: %s' % err)

        return kwargs
