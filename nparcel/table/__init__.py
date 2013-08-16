__all__ = [
    "Table",
]
import re


class Table(object):
    """Base Nparcel DB table.
    """

    def __init__(self, name):
        self.name = name

    def insert_sql(self, kwargs):
        """
        """
        columns = kwargs.keys()
        values = [kwargs.get(x) for x in columns]
        escaped_values = []
        cleansed_values = []

        # Escape single quotes.
        for value in values:
            new_value = value
            if isinstance(value, str):
                new_value = re.sub("'", "''", value)

            escaped_values.append(new_value)

        # Enclose strings with quotes.
        for value in escaped_values:
            new_value = value
            if isinstance(value, str):
                new_value = "'%s'" % value

            cleansed_values.append(new_value)

        sql = """INSERT INTO %s (%s)
VALUES (%s)""" % (self.name,
                  ', '.join(columns),
                  ', '.join(map(str, cleansed_values)))

        return sql
