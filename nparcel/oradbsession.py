ora__all__ = [
    "oradbsession",
]
import sqlite
import datetime
import cx_Oracle

import nparcel
from nparcel.utils.log import log


class OraDbSession(object):
    """Oracle DB session manager.

    .. attribute:: connection

        Database connection object.  Handles a :mod:`cx_Oracle.Connection`
        object

    .. attribute:: cursor

        Database cursor object.  Handles a :mod:`cx_Oracle.Cursor` object
        based on :attr:`connection`

    .. attribute:: transsend

        TransSend database ORM object based on :mod:`nparcel.TransSend`

    """
    _connection = None
    _cursor = None
    _transsend = nparcel.TransSend()
    _host = None
    _database = None
    _user = None
    _password = None
    _port = None
    _sid = None

    def __init__(self, kwargs=None):
        if kwargs is not None:
            self._host = kwargs.get('host')
            self._database = kwargs.get('database')
            self._user = kwargs.get('user')
            self._password = kwargs.get('password')
            self._port = kwargs.get('port')
            if self._port is not None:
                try:
                    self._port = int(self._port)
                except ValueError, e:
                    log.error('Port "%s" could not cast to int: %s' % e)
            self._sid = kwargs.get('sid')

    def __call__(self, sql=None):
        if sql is not None:
            try:
                log.debug('Executing SQL:\n%s' % sql)
                self.cursor.execute(sql)
            except Exception, e:
                if self.connection is not None:
                    log.error('ODBC error: %s' % str(e))
                pass
        else:
            # This is a link check.
            return self.connection is not None

    @property
    def database(self):
        return self._database

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def port(self):
        return self._port

    @property
    def sid(self):
        return self._sid

    @property
    def row(self):
        return self.cursor.fetchone()

    @property
    def host(self):
        return self._host

    @property
    def cursor(self):
        return self._cursor

    def set_cursor(self, value):
        self._cursor = value

    @property
    def connection(self):
        return self._connection

    def set_connection(self, value):
        self._connection = value

    @property
    def transsend(self):
        return self._transsend

    @property
    def conn_string(self):
        return '%s/%s@%s:%d/%s' % (self.user,
                                   self.password,
                                   self.host,
                                   self.port,
                                   self.sid)

    def date_now(self, *args):
        """Helper method that returns the current time stamp in a format
        suitable for the database.

        """
        time = datetime.datetime.now().isoformat(' ')

        # Strip of last 3 digits of precision for MSSQL.
        return time[:-3]

    def rows(self):
        """
        """
        for row in self.cursor.fetchall():
            yield row

    def set_connection(self, value):
        self._connection = value

    def connect(self):
        """Create a database session connection based on class attributes.

        """
        log.info('Attempting database connection ...')
        status = False

        if self.host is None:
            log.info('DB session (sqlite) -- starting ...')
            self.set_connection(sqlite.connect(':memory:'))
        else:
            try:
                log.info('DB session (Oracle) -- starting ...')
                self.set_connection(cx_Oracle.connect(self.conn_string))
            except cx_Oracle.DatabaseError, err:
                log.error('DB connection failed: %s' % str(err).rstrip())

        if self.connection is not None:
            self.set_cursor(self.connection.cursor())
            log.info('DB session creation OK')
            if self.host is not None:
                self('ALTER SESSION SET CURRENT_SCHEMA = transsendops_prd')

        return status

    def disconnect(self):
        """Disconnect from the database.

        """
        log.info('Disconnecting from DB ...')
        if self.connection is not None:
            self.cursor.close()
            self.set_cursor(None)
            self.connection.close()
            self.set_connection(None)
        else:
            log.warn('No DB connection detected')

    def create_table(self, name, schema):
        """We'd only expect to create tables for testing purposes only.
        """
        log.info('Creating table "%s" ...' % name)
        log.debug('Schema list "%s"' % ",\n".join(schema))
        dml = """CREATE TABLE %s (%s)""" % (name, ",\n".join(schema))
        self.cursor.execute(dml)
        self.connection.commit()

    def insert(self, sql):
        """Insert a record and return the new row id.

        .. note::
            Not enabled for Oracle.

        """
        id = None

        self(sql)

        # sqlite and MSSQL implement this differently.
        if self.host is None:
            self('SELECT last_insert_rowid()')

        id = self.cursor.fetchone()[0]

        return id

    def commit(self):
        """Commit the database state.

        .. note::
            Not enabled for Oracle.

        """
        if self.host is None:
            # sqlite.
            self.connection.commit()

    def rollback(self):
        """Rollback the database state.

        .. note::
            Not enabled for Oracle.

        """
        log.debug('Rolling back DB state')
        if self.host is None:
            # sqlite.
            self.connection.rollback()

    def columns(self):
        """Return a list of column names within the current cursor context.
        """
        return list(map(lambda x: x[0].lower(), self.cursor.description))

    def load_fixture(self, table, fixture):
        """Load a *fixture* file into a *table*

        **Args:**
            *table*: a table ORM oject to load the fixture into

            *fixture*: name of the fixture file.

        """
        table_name = table.name
        log.info('Loading fixture file "%s" into table "%s"' %
                 (fixture, table_name))

        fh = None
        try:
            fh = open(fixture)
        except IOError, e:
            log.error('Fixture file "%s" error' % (fixture, e))

        if fh is not None:
            items = eval(fh.read())
            for i in items:
                sql = table.insert_sql(i)
                self(sql)
