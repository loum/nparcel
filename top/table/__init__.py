__all__ = [
    "Table",
]
import re

from top.utils.log import log


class Table(object):
    """Base DB table.
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
        """Build an SQL DML insert statement based on the *kwargs*
        dictionary.  The *kwargs* keys are the table column names whilst the
        *kwargs* values are the values to insert into the the table column.

        Performs a preliminary check of the *kwargs* values to ensure
        that they are SQL safe.  See :method:`sanitise` for more
        information.

        **Kwargs:**
            *kwargs*: the table column name and values to insert

        **Returns:**
            an SQL DML insert string

        """
        columns = kwargs.keys()
        values = self.sanitise([kwargs.get(x) for x in columns])

        sql = """INSERT INTO %s (%s)
VALUES (%s)""" % (self.name, ', '.join(columns), values)

        return sql

    def update_sql(self, kwargs, where_column='id', keys=None):
        """Build an SQL DML update statement based on the *kwargs*
        dictionary.  The *kwargs* keys are the table column names whilst the
        *kwargs* values are the values to insert into the the table column.

        Performs a preliminary check of the *kwargs* values to ensure
        that they are SQL safe.  See :method:`sanitise` for more
        information.

        **Args:**
            *kwargs*: the table column name and values to insert

        **Kwargs:**
            *where_column*: the table column to use in the WHERE clause.
            Typically, we expect the table's primary key.
            Defaults to ``id``

            *keys*: tuple of integers to update

        **Returns:**
            an SQL DML update string

        """
        columns = kwargs.keys()
        values = self.sanitise([kwargs.get(x) for x in columns],
                               as_string=False)
        set_clause_dict = dict(zip(columns, values))

        set_clause = ['%s=%s' % (k, v) for k, v in set_clause_dict.iteritems()]

        where_clause = str()
        if keys is not None:
            if len(keys) == 1:
                keys = "(%d)" % keys[0]
            else:
                keys = str(keys)
            where_clause = 'WHERE %s IN %s' % (where_column, keys)

        sql = """UPDATE %s
SET %s
%s""" % (self.name, ', '.join(set_clause), where_clause)

        return sql

    def sanitise(self, values, as_string=True):
        """Prepares raw data for safe use in an SQL DML.

        Scenarios that are catered for include:

        * escape single quote or apostrophe.  For example, "can't" becomes
        "can''t"

        * enclose strings with quotes.  For example, "banana" becomes
        "'banana'"

        **Args:**
            *values*: list of table values that will form the SQL DML.
            For example, [1, 'dummy']

        **Returns:**
            string representation of the *values* in a format that is
            SQL DML safe.  For example, ``[1, 'dummy']`` becomes
            ``"1, 'dummy'"``

        """
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
                if value != 'NULL':
                    new_value = "'%s'" % value
                else:
                    new_value = value

            cleansed_values.append(new_value)

        values = cleansed_values
        if as_string:
            values = ', '.join(map(str, cleansed_values))

        return values
