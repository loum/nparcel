ora__all__ = [
    "oradbsession",
]
import sqlite
import datetime

#import nparcel
from nparcel.utils.log import log


class OraDbSession(object):
    """Oralce DB session manager.
    """
    _connection = None
    _cursor = None

    def __init__(self, **kwargs):
        self._host = kwargs.get('host')
        self._driver = kwargs.get('driver')
        self._database = kwargs.get('database')
        self._user = kwargs.get('user')
        self._password = kwargs.get('password')
        self._port = kwargs.get('port')

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
    def driver(self):
        return self._driver

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

    @property
    def job(self):
        return self._job

    @property
    def jobitem(self):
        return self._jobitem

    @property
    def identity_type(self):
        return self._identity_type

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

        try:
            if self.host is None:
                log.info('DB session (sqlite) -- starting ...')
                self.set_connection(sqlite.connect(':memory:'))

            self.set_cursor(self.connection.cursor())
            log.info('DB session creation OK')
            status = True
        except Exception, e:
            log.error('Database session creation failed: "%s"' % str(e))
            pass

        return status

    def create_table(self, name, schema):
        """We'd only expect to create tables for testing purposes only.
        """
        log.info('Creating table "%s" ...' % name)
        log.debug('Schema list "%s"' % ",\n".join(schema))
        dml = """CREATE TABLE %s (%s)""" % (name, ",\n".join(schema))
        self.cursor.execute(dml)
        self.connection.commit()

    def close(self):
        if self.connection is not None:
            self._cursor = None
            self.connection.close()
            self._connection = None

    def insert(self, sql):
        """
        """
        id = None

        self(sql)

        # sqlite and MSSQL implement this differently.
        if self.host is None:
            self('SELECT last_insert_rowid()')
        else:
            self('SELECT SCOPE_IDENTITY()')

        id = self.cursor.fetchone()[0]

        return id

    def commit(self):
        """
        """
        if self.host is None:
            # sqlite.
            self.connection.commit()
        else:
            # MSSQL.
            self('COMMIT TRANSACTION')

    def columns(self):
        """Return a list of column names within the current cursor context.
        """
        return list(map(lambda x: x[0], self.cursor.description))
