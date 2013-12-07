__all__ = [
    "dbsession",
]
import sqlite
import pyodbc
import datetime

import nparcel
from nparcel.utils.log import log


class DbSession(object):
    """Nparcel DB session manager.
    """
    _connection = None
    _cursor = None
    _job = nparcel.Job()
    _jobitem = nparcel.JobItem()
    _agent = nparcel.Agent()
    _agent_stocktake = nparcel.AgentStocktake()
    _identity_type = nparcel.IdentityType()

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
            except pyodbc.ProgrammingError, e:
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
    def agent(self):
        return self._agent

    @property
    def agent_stocktake(self):
        return self._agent_stocktake

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
        status = False

        try:
            if self.host is None:
                log.info('DB session (sqlite) -- starting ...')
                self.set_connection(sqlite.connect(':memory:'))
            else:
                log.info('DB session (MSSQL) -- starting ...')
                conn_string = ('%s;%s;%s;%s;%s;%s;%s' %
                               ('DRIVER={%s}' % self.driver,
                                'Server=%s' % self.host,
                                'Database=%s' % self.database,
                                'UID=%s' % self.user,
                                'PWD=%s' % self.password,
                                'port=%d' % self.port,
                                'autocommit=False'))
                self.set_connection(pyodbc.connect(conn_string))

            self.set_cursor(self.connection.cursor())
            log.info('DB session creation OK')

            if self.host is None:
                # For testing, create the tables.
                self.create_test_table()
            else:
                # For MSSQL, we want to control commits.
                self('SET IMPLICIT_TRANSACTIONS ON')

            status = True
        except pyodbc.Error, e:
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

    def create_test_table(self):
        """
        """
        self.create_table("job", self._job.schema)
        self.create_table("job_item", self.jobitem.schema)
        self.create_table("agent", self._agent.schema)
        self.create_table("identity_type", self._identity_type.schema)
        self.create_table("agent_stocktake", self._agent_stocktake.schema)

    def disconnect(self):
        log.info('Disconnecting from DB ...')
        if self.connection is not None:
            self._cursor.close()
            self._cursor = None
            self.connection.close()
            self._connection = None
        else:
            log.warn('No DB connection detected')

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

    def rollback(self):
        """
        """
        log.debug('Rolling back DB state')
        if self.host is None:
            # sqlite.
            self.connection.rollback()
        else:
            # MSSQL.
            self('ROLLBACK TRANSACTION')

    def columns(self):
        """Return a list of column names within the current cursor context.
        """
        return list(map(lambda x: x[0], self.cursor.description))

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
            log.error('Fixture file "%s" error: %s' % (fixture, e))

        if fh is not None:
            items = eval(fh.read())
            for i in items:
                sql = table.insert_sql(i)
                self(sql)
