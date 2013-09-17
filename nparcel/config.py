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

    def proxy_kwargs(self):
        """Extract proxy connectivity information from the configuration.

        Proxy connectivity information is taken from the ``[proxy]``
        section in the configuration file.  A typical example is::

            [proxy]
            host = auproxy-farm.toll.com.au
            user = <username>
            password = <passwd>
            port = 8080
            protocol = https

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'host': ...,
                        'user': ...,
                        'password': ...,
                        'port': ...,
                        'protocol': ...}

        """
        kwargs = None

        try:
            host = self.get('proxy', 'host')
            user = self.get('proxy', 'user')
            password = self.get('proxy', 'password')
            port = self.get('proxy', 'port')
            if port is not None and port:
                port = int(port)
            protocol = self.get('proxy', 'protocol')
            kwargs = {'host': host,
                      'user': user,
                      'password': password,
                      'port': port,
                      'protocol': protocol}
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.error('Config proxy: %s' % err)

        return kwargs

    def proxy_string(self, kwargs=None):
        """Constructs a proxy string based on the *kwargs* dictionary
        structure or :attr:`proxy` attribute (in that order if *kwargs* is
        ``None``).

        **Kwargs:**
            *kwargs* as per the return value of the :meth:`proxy_kwargs`
            method

        **Returns:**
            string that could be fed directly into a HTTP/S header
            to handle proxy authentication in the request.  Example::

                http://loumar:<passwd>@auproxy-farm.toll.com.aus:8080

        """
        values = None
        if kwargs is not None:
            values = kwargs
        else:
            values = self.proxy_kwargs()
        proxy = None
        if values is not None:
            # Check if we have a username and password.
            if (values.get('user') is not None and
                values.get('password') is not None):
                proxy = ("%s:%s@" % (values.get('user'),
                                     values.get('password')))

            if values.get('host') is not None:
                proxy += values.get('host')

            if values.get('port') is not None:
                proxy += ':' + str(values.get('port'))

        return proxy
