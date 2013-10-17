__all__ = [
     "Mts",
]
import ConfigParser
import cx_Oracle
import os
import datetime

import nparcel
from nparcel.utils.log import log


class Mts(object):
    """Nparcel Mts class.

    .. attribute:: config

        :mod:`nparcel.Config` object

    .. attribute:: db

        database object

    """
    _config = nparcel.Config()
    _db = {}
    _conn = None
    _cursor = None
    _template_dir = os.path.join(os.path.expanduser('~'),
                                 '.nparceld',
                                 'templates')

    def __init__(self,
                 config='npmts.conf'):
        """Nparcel Mts initialisation.
        """
        self._config.set_config_file(config)

    @property
    def config(self):
        return self._config

    @property
    def template_dir(self):
        return self._template_dir

    def set_template_dir(self, value):
        self._template_dir = value

    @property
    def conn_string(self):
        db_kwargs = self.db_kwargs()

        host = db_kwargs.get('host')
        user = db_kwargs.get('user')
        password = db_kwargs.get('password')
        port = db_kwargs.get('port')
        sid = db_kwargs.get('sid')

        return '%s/%s@%s:%d/%s' % (user, password, host, port, sid)

    def db_kwargs(self):
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

    def set_db_kwargs(self, **kwargs):
        self._db_kwargs = kwargs

    def connect(self):
        """Make a connection to the database.

        """
        self._conn = cx_Oracle.connect(self.conn_string)
        self._cursor = self._conn.cursor()

    def disconnect(self):
        """Disconnect from the database.

        """
        self._conn.close()

        self._cursor = None
        self._conn = None

    @property
    def db_version(self):
        self._cursor.execute('SELECT version FROM V$INSTANCE')

        for row in self._cursor:
            print('Oracle DB Version: %s' % row)

    def get_delivery_report_sql(self, base_dir=None):
        """

        **Kwargs:**
            base_dir: override the standard location to search for the

        """
        to_dt = datetime.datetime.now()
        from_dt = to_dt - datetime.timedelta(seconds=86400)

        to_date = to_dt.strftime('%d/%m/%Y')
        from_date = from_dt.strftime('%d/%m/%Y')

        sql = None

        sql = self.load_template('mts_sql.t',
                                 base_dir=base_dir,
                                 to_date=to_date,
                                 from_date=from_date)

        log.debug('SQL: %s' % sql)

        return sql
