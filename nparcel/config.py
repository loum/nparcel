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
        if self._config_file is not None:
            self.set_config_file(self._config_file)

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

    def db_kwargs(self):
        """Extract database connectivity information from the configuration.

        Database connectivity information is taken from the ``[db]``
        section in the configuration file.  A typical example is::

            [db]
            driver = FreeTDS
            host = SQVDBAUT07
            database = Nparcel
            user = npscript
            password = <passwd>
            port =  1442

        Base assumptions on "host" keyword.  No "host" means this must be a
        test scenario in which case the database session is a memory-based
        sqlite instance.

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'driver': ...,
                          'host': ...,
                          'database': ...,
                          'user': ...,
                          'password': ...,
                          'port': ...}

        """
        kwargs = None

        try:
            host = self.get('db', 'host')
            driver = self.get('db', 'driver')
            database = self.get('db', 'database')
            user = self.get('db', 'user')
            password = self.get('db', 'password')
            port = self.get('db', 'port')
            if port is not None and port:
                port = int(port)
            kwargs = {'driver': driver,
                      'host': host,
                      'database': database,
                      'user': user,
                      'password': password,
                      'port': port}
        except ConfigParser.NoOptionError, err:
            log.error('Missing DB key via config: %s' % err)

        return kwargs
