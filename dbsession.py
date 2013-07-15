__all__ = [
    "dbsession",
]
import sqlite
from nparcel.utils.log import log

import nparcel


class DbSession(object):
    """Nparcel DB session manager.
    """

    def __init__(self,
                 host='localhost'):
        self._host = host
        self._connection = None
        self._cursor = None
        self._job = nparcel.Job()
        self._job_item = nparcel.JobItem()

    def __call__(self, sql):
        log.debug('Executing SQL:\n%s' % sql)
        if self.host == 'localhost':
            self.cursor.execute(sql)

    def rows(self):
        """
        """
        for row in self.cursor.fetchall():
            yield row

    def commit(self):
        """
        """
        self.connection.commit()

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

    def connect(self):
        """Create a database session connection based on class attributes.

        """
        try:
            if self.host == 'localhost':
                self.set_connection(sqlite.connect(':memory:'))
                self.set_cursor(self.connection.cursor())
                log.info('sqlite DB session creation OK')

                # For testing, create the tables.
                self.create_test_table()
            else:
                log.info('MSSQL DB session creation OK -- TODO')
        except Exception, e:
            log.error('Database session creation failed: "%s"' % str(e))
            pass

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
        self.create_table("job_item", self._job_item.schema)

    def close(self):
        if self.connection is not None:
            self.connection.close()

    def insert(self, sql):
        """
        """
        id = None

        if self.host == 'localhost':
            self(sql)
            self('SELECT last_insert_rowid()')
            id = self.cursor.fetchone()[0]

        return id

    def create(self, job_data, job_item_data):
        """
        """
        log.debug('Creating Nparcel record with following data ...')
        job_id = self.insert(self._job.insert(job_data))
        log.debug('"job.id" created %d' % job_id)

        # Set the "job_item" table's foreign key.
        job_item_data['job_id'] = job_id
        job_item_id = self.insert(self._job_item.insert(job_item_data))
        log.debug('"job_item.id" created %d' % job_item_id)
