__all__ = [
    "dbsession",
]
import sqlite
import pyodbc
from nparcel.utils.log import log

import nparcel


class DbSession(object):
    """Nparcel DB session manager.
    """

    def __init__(self, **kwargs):
        self._host = kwargs.get('host')
        self._driver = kwargs.get('driver')
        self._database = kwargs.get('database')
        self._user = kwargs.get('user')
        self._password = kwargs.get('password')
        self._port = kwargs.get('port')

        self._connection = None
        self._cursor = None
        self._job = nparcel.Job()
        self._jobitem = nparcel.JobItem()
        self._agent = nparcel.Agent()
        self._identity_type = nparcel.IdentityType()

    def __call__(self, sql=None):
        if sql is not None:
            try:
                log.debug('Executing SQL:\n%s' % sql)
                self.cursor.execute(sql)
            except pyodbc.ProgrammingError, e:
                if self.connection is not None:
                    log.error('ODBC error: %s' % str(e))
                    # Gracefully close the connection.
                    self.close()
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

    def rows(self):
        """
        """
        for row in self.cursor.fetchall():
            yield row

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

    def create(self, job_data, jobitem_data):
        """
        **Args:**
            job_data: dictionary of the "job" table fields

            jobitem_data: dictionary of the "jobitem" table fields

        """
        job_id = self.insert(self._job.insert_sql(job_data))
        log.debug('"job.id" %d created' % job_id)

        # Set the "jobitem" table's foreign key.
        jobitem_data['job_id'] = job_id
        jobitem_id = self.insert(self.jobitem.insert_sql(jobitem_data))
        log.debug('"jobitem.id" %d created' % jobitem_id)

    def update(self, job_id, agent_id, jobitem_data):
        """
        **Args:**
            job_id: row ID of the "job" table

            agent_id: row ID of the "agent" table

            jobitem_data: dictionary of the "jobitem" table fields

        """
        sql = self._job.update_sql(job_id, agent_id)
        self(sql)

        # Set the "jobitem" table's foreign key.
        jobitem_data['job_id'] = job_id
        jobitem_id = self.insert(self.jobitem.insert_sql(jobitem_data))
        log.debug('"jobitem.id" %d created' % jobitem_id)

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
        if self.host is None:
            # sqlite.
            self.connection.rollback()
        else:
            # MSSQL.
            self('ROLLBACK TRANSACTION')
