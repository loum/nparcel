__all__ = [
    "Table",
]
import re

from nparcel.utils.log import log


class Table(object):
    """Base Nparcel DB table.
    """
    _name = None
    _alias = None

    def __init__(self, name, alias=None):
        self._name = name
        if alias is not None:
            self._alias = alias

    @property
    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value
        log.debug('Set table name to "%s"' % self._name)

    @property
    def alias(self):
        return self._alias

    def set_alias(self, value):
        self._alias = value
        log.debug('Set table alias to "%s"' % self._alias)

    def insert_sql(self, kwargs):
        """
        """
        columns = kwargs.keys()
        values = [kwargs.get(x) for x in columns]
        escaped_values = []
        cleansed_values = []

        for value in values:
            new_value = value
            if isinstance(value, str):
                # Escape single quotes.
                new_value = re.sub("'", "''", value)

            escaped_values.append(new_value)

        # Enclose strings with quotes.
        for value in escaped_values:
            new_value = value
            if isinstance(value, str):
                new_value = "'%s'" % value

            cleansed_values.append(new_value)

        values = ', '.join(map(str, cleansed_values))
        values = values.replace("'NULL'", "NULL")
        sql = """INSERT INTO %s (%s)
VALUES (%s)""" % (self.name,
                  ', '.join(columns),
                  values)

        return sql
