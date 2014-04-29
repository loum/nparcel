__all__ = [
    "ReturnsReference",
]
import top


class ReturnsReference(top.Table):
    """ReturnsReference table ORM.
    """

    def __init__(self):
        """ReturnsReference initialiser.
        """
        super(ReturnsReference, self).__init__(name='returns_reference',
                                               alias='rr')

    @property
    def schema(self):
        return('id INTEGER PRIMARY KEY',
               'returns_id INTEGER',
               'reference_nbr TEXT(32)')

    def reference_nbr_sql(self, returns_id, alias=None, db='sqlite'):
        """SQL wrapper to extract the ``returns_reference.reference_nbr``
        of items relating to *returns_id*.

        **Args:**
            *returns_id*: value relating to the ``returns.id`` column

        **Kwargs:**
            *alias*: override the :attr:`alias` value

            *db*: the type of DB connection

        **Returns:**
            the SQL string

        """
        old_alias = self.alias
        if alias is not None:
            self.set_alias(alias)

        sql = """SELECT %(alias)s.reference_nbr
FROM %(name)s AS %(alias)s
WHERE returns_id = %(id)d""" % {'name': self.name,
                                'alias': self.alias,
                                'id': returns_id}

        self.set_alias(old_alias)

        return sql
