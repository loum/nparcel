__all__ = [
    "AgentStocktake",
]
import nparcel


class AgentStocktake(nparcel.Table):
    """AgentStocktake DB table ORM.
    """

    def __init__(self):
        """
        """
        super(AgentStocktake, self).__init__(name='agent_stocktake')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "agent_id INTEGER",
                "created_ts TIMESTAMP",
                "reference_nbr TEXT(32)",
                "processed_ts CHAR(6)"]

    def reference_sql(self, alias='st'):
        """Extract ``agent_stocktake.reference_nbr`` records that have not
        been processed (``agent_stocktake.processed_ts`` is ``NULL``).

        **Kwargs:**
            *alias*: table alias (default ``st``)

        **Returns:**
            the SQL string

        """
        sql = """SELECT DISTINCT %(alias)s.reference_nbr
FROM %(name)s as %(alias)s
WHERE %(alias)s.processed_ts IS NULL""" % {'name': self.name,
                                           'alias': alias}

        return sql
