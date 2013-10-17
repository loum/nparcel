__all__ = [
     "Mts",
]
import ConfigParser

import nparcel
from nparcel.utils.log import log


class Mts(nparcel.Service):
    """Nparcel Mts class.
    """

    def __init__(self,
                 config='npmts.conf'):
        """Nparcel Mts initialisation.
        """
        self._config = nparcel.Config()
        self._config.set_config_file(config)

        db = None

        super(nparcel.Mts, self).__init__(db=db)

    @property
    def config(self):
        return self._config

    @property
    def conn_string(self):
        db_kwargs = self._db_kwargs()

        host = db_kwargs.get('host')
        user = db_kwargs.get('user')
        password = db_kwargs.get('password')
        port = db_kwargs.get('port')
        sid = db_kwargs.get('sid')

        return '%s/%s@%s:%d/%s' % (user, password, host, port, sid)

    def _db_kwargs(self):
        """Extract database connectivity information from the configuration.

        Database connectivity information is taken from the ``[db]``
        section in the configuration file.  A typical example is::

            [db]
            host = tsspodb2
            user = TOLL_DW_MTS
            password = <password>
            port =  1521
            database = GC3DW

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'host': ...,
                          'user': ...,
                          'password': ...,
                          'port': ...,
                          'database': ...}

        """
        db_kwargs = None

        try:
            host = self.config.get('db', 'host')
            user = self.config.get('db', 'user')
            password = self.config.get('db', 'password')
            port = self.config.get('db', 'port')
            sid = self.config.get('db', 'sid')

            if port is not None:
                port = int(port)
            db_kwargs = {'host': host,
                         'user': user,
                         'password': password,
                         'port': port,
                         'sid': sid}
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.info('Missing DB key via config: %s' % err)

        return db_kwargs
