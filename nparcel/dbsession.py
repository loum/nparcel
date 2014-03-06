__all__ = [
    "dbsession",
]
from nparcel.utils.log import log
try:
    from pysqlite2 import dbapi2 as sqlite3
except:
    import sqlite as sqlite3
import pyodbc
import datetime

import nparcel


class DbSession(object):
    """Nparcel DB session manager.

    .. attribute:: db_type

        string value that captures the database type (for example,
        ``sqlite`` or ``MSSQL``)

    """
    _connection = None
    _cursor = None
    _db_type = None
    _job = nparcel.Job()
    _jobitem = nparcel.JobItem()
    _agent = nparcel.Agent()
    _agent_stocktake = nparcel.AgentStocktake()
    _identity_type = nparcel.IdentityType()
    _parcel_size = nparcel.ParcelSize()
    _delivery_partner = nparcel.DeliveryPartner()
    _login_account = nparcel.LoginAccount()
    _system_level_access = nparcel.SystemLevelAccess()
    _login_access = nparcel.LoginAccess()
    _returns = nparcel.Returns()
    _returns_reference = nparcel.ReturnsReference()

    def __init__(self, **kwargs):
        self._host = kwargs.get('host')
        self._driver = kwargs.get('driver')
        self._database = kwargs.get('database')
        self._user = kwargs.get('user')
        self._password = kwargs.get('password')
        self._port = kwargs.get('port')

    def __call__(self, sql=None):
        """Class callable that can execute *sql* or perform a simple
        connection check if *sql* is ``None``.

        **Kwargs:**
            *sql*: the SQL string to execute

        **Returns:**
            boolean ``True`` if the connection is alive

            boolean ``False`` otherwise

        """
        is_alive = False

        if sql is not None:
            try:
                log.debug('Executing SQL:\n%s' % sql)
                try:
                    self.cursor.execute(sql)
                    is_alive = True
                except Exception, err:
                    log.error('SQL "%s" failed: %s' % (sql, err))
            except pyodbc.ProgrammingError, e:
                if self.connection is not None:
                    log.error('ODBC error: %s' % str(e))
                pass
        else:
            # This is a link check.
            is_alive = self.connection is not None
            log.debug('DB connection alive? %s' % is_alive)

        return is_alive

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
    def db_type(self):
        return self._db_type

    def set_db_type(self, value):
        self._db_type = value
        log.debug('Set DB type to "%s"' % self.db_type)

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

    @property
    def parcel_size(self):
        return self._parcel_size

    @property
    def delivery_partner(self):
        return self._delivery_partner

    @property
    def login_account(self):
        return self._login_account

    @property
    def system_level_access(self):
        return self._system_level_access

    @property
    def login_access(self):
        return self._login_access

    @property
    def returns(self):
        return self._returns

    @property
    def returns_reference(self):
        return self._returns_reference

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
                log.info('DB session (sqlite3) -- starting ...')
                self.set_connection(sqlite3.connect(':memory:'))
                self.connection.text_factory = str
                self.set_db_type('sqlite3')
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
                self.set_db_type('MSSQL')

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
        self.create_table('job', self.job.schema)
        self.create_table('job_item', self.jobitem.schema)
        self.create_table('agent', self.agent.schema)
        self.create_table('identity_type', self.identity_type.schema)
        self.create_table('agent_stocktake', self.agent_stocktake.schema)
        self.create_table('parcel_size', self.parcel_size.schema)
        self.create_table('delivery_partner', self.delivery_partner.schema)
        self.create_table('login_account', self.login_account.schema)
        self.create_table('system_level_access',
                          self.system_level_access.schema)
        self.create_table('login_access', self.login_access.schema)
        self.create_table('returns', self.returns.schema)
        self.create_table('returns_reference',
                          self.returns_reference.schema)

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
        cols = []
        if self.cursor.description is not None:
            cols = list(map(lambda x: x[0], self.cursor.description))

        return cols

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
