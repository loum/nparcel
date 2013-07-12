__all__ = [
    "dbsession",
]
import sqlite
from nparcel.utils.log import log


class DbSession(object):
    """Nparcel DB session manager.
    """

    def __init__(self,
                 host='localhost'):
        self._host = host
        self._connection = None
        self._cursor = None

    def __call__(self, sql):
        log.debug('Executing SQL: %s' % sql)
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
            else:
                log.info('MSSQL DB session creation OK -- TODO')
        except:
            log.error('Database session creation failed')
            pass

    def create_table(self, name, schema):
        """We'd only expect to create tables for testing purposes only.
        """
        log.info('Creating table "%s" ...' % name)
        log.debug('schema list "%s"' % ",\n".join(schema))

        self.cursor.execute("""CREATE TABLE %s (%s)""" % (name,
                                                          ",\n".join(schema)))
        self.connection.commit()

    def close(self):
        if self.connection is not None:
            self.connection.close()
