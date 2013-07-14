__all__ = [
    "Table",
]
from nparcel.utils.log import log


class Table(object):
    """Base Nparcel DB table.
    """

    def __init__(self, name):
        self.name = name

    def insert(self, kwargs):
        """
        """
        columns = kwargs.keys()
        values = [kwargs.get(x) for x in columns]

        sql = """
INSERT INTO %s (%s)
VALUES ("%s")""" % (self.name, ", ".join(columns), ", ".join(values))
        log.debug('"%s" table generated SQL: "%s"' % (self.name, sql))

        return sql
