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
        cleansed_values = []

        # Enclose strings with quotes.
        for value in values:
            new_value = value
            if isinstance(value, str):
                new_value = '"%s"' % value

            cleansed_values.append(new_value)

        sql = """
INSERT INTO %s (%s)
VALUES (%s)""" % (self.name,
                    ", ".join(columns),
                    ', '.join(map(str, cleansed_values)))
        log.debug('"%s" table generated SQL: "%s"' % (self.name, sql))

        return sql
