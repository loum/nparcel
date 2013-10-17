__all__ = [
     "Mts",
]
import ConfigParser
import cx_Oracle
import os
import datetime

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import load_template


class Mts(object):
    """Nparcel Mts class.

    .. attribute:: config

        :mod:`nparcel.Config` object

    .. attribute:: db

        database object

    .. attribute:: report_range

        number (float) of days that the report should cover (default 7
        days).  Supports precision values such as 2.5 (which evaluates
        to two and one half days)

    .. attribute:: display_headers

        boolean control whether the column names are added to the CSV

    .. attribute:: out_dir

        location to where the CSV report files are written

    """
    _config = nparcel.Config()
    _db = {}
    _conn = None
    _cursor = None
    _template_dir = os.path.join(os.path.expanduser('~'),
                                 '.nparceld',
                                 'templates')
    _report_range = 7
    _display_headers = True
    _out_dir = '/data/nparcel/mts'

    def __init__(self, config='npmts.conf'):
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
    def report_range(self):
        return self._report_range

    def set_report_range(self, value):
        self._report_range = float(value)

    @property
    def display_headers(self):
        return self._display_headers

    def set_display_headers(self, value):
        self._display_headers = (value.lower == 'yes')

    @property
    def out_dir(self):
        return self._out_dir

    def set_out_dir(self, value):
        self._out_dir = value

    @property
    def conn_string(self):
        db_kwargs = self.db_kwargs()

        host = db_kwargs.get('host')
        user = db_kwargs.get('user')
        password = db_kwargs.get('password')
        port = db_kwargs.get('port')
        sid = db_kwargs.get('sid')

        return '%s/%s@%s:%d/%s' % (user, password, host, port, sid)

    def _parse_config(self):
        """Read config items from the configuration file.

        Each section that starts with ``ftp_`` are interpreted as an FTP
        connection to process.

        """
        self.config.parse_config()

        # Report range.
        try:
            self.set_report_range(self.config.get('settings',
                                                  'report_range'))
            log.debug('Report range: %s' % self.report_range)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.info('Using default report range %s (days)' %
                     self.report_range)

        # Display headers.
        try:
            self.set_display_headers(self.config.get('settings',
                                                     'display_headers'))
            log.debug('Display headers: %s' % self.display_headers)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.info('Using default report range %s (days)' %
                     self.report_range)

        # Output directory.
        try:
            self.set_out_dir(self.config.get('settings', 'out_dir'))
            log.debug('Report output director: %s' % self.out_dir)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.info('Using default output directory %s' % self.out_dir)

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
        """Get the SQL query string that generates the delivery report.

        **Kwargs:**
            base_dir: override the standard location to search for the

        **Returns:**
            the delivery report SQL string

        """
        to_dt = datetime.datetime.now()
        seconds = self.report_range * 86400
        from_dt = to_dt - datetime.timedelta(seconds=int(seconds))

        to_date = to_dt.strftime('%d/%m/%Y')
        from_date = from_dt.strftime('%d/%m/%Y')

        sql = None

        sql = load_template('mts_sql.t',
                            base_dir=base_dir,
                            to_date=to_date,
                            from_date=from_date)

        log.debug('SQL: %s' % sql)

        return sql
