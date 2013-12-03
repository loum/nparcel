__all__ = [
    "AgentStocktake",
]
import datetime

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

    def reference_sql(self, day_range=7, alias='st'):
        """Extract ``agent_stocktake.reference_nbr`` records that have not
        been processed (``agent_stocktake.processed_ts`` is ``NULL``).

        **Kwargs:**
            *day_range*: number of days from current time to include
            in search (default 7.0 days)

            *alias*: table alias (default ``st``)

        **Returns:**
            the SQL string

        """
        now = datetime.datetime.now()
        start_ts = now - datetime.timedelta(days=day_range)
        start_date = start_ts.strftime('%Y-%m-%d %H:%M:%S')

        sql = """SELECT DISTINCT %(alias)s.reference_nbr
FROM %(name)s as %(alias)s
WHERE %(alias)s.processed_ts IS NULL
AND created_ts > '%(start_date)s'""" % {'name': self.name,
                                        'alias': alias,
                                        'start_date': start_date}

        return sql
