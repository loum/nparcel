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
                "agent_id TEXT(6)",
                "created_ts TIMESTAMP",
                "reference_nbr TEXT(32)",
                "processed_ts CHAR(6)"]

    def reference_sql(self, day_range=7, alias='st'):
        """Extract ``agent_stocktake.reference_nbr`` records within
        *day_range* days from now.

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
WHERE created_ts > '%(start_date)s'""" % {'name': self.name,
                                          'alias': alias,
                                          'start_date': start_date}

        return sql

    def update_processed_ts_sql(self, ts_string):
        """Update the ``agent_stocktake.processed_ts`` to the
        :mod:`datetime` structure denoted by *ts_string* (where the current
        column value is NULL).

        **Args:**
            *ts_string*: string representation of time in ISO format.
            For example, ``2013-12-04 12:00:00``

        **Kwargs:**
            *day_range*: number of days from current time to include
            in search (default 7.0 days)

        **Returns:**
            the SQL string

        """
        sql = """UPDATE %(name)s
SET processed_ts = '%(ts)s'
WHERE processed_ts IS NULL""" % {'name': self.name,
                                 'ts': ts_string}

        return sql

    def compliance_sql(self, period=7, alias='st'):
        """Select agent information of agents that have not performed
        a stocktake since *period* days prior.

        **Kwargs:**
            *period*: time (in days) from now that is the cut off for
            agent compliance (default 7 days)

            *alias*: table alias (default ``st``)

        **Returns:**
            the SQL string

        """
        now = datetime.datetime.now()
        compliance_ts = now - datetime.timedelta(days=period)
        compliance_date = compliance_ts.strftime('%Y-%m-%d %H:%M:%S')

        sql = """SELECT ag.dp_code as DP_CODE,
ag.code as AGENT_CODE,
ag.name as AGENT_NAME,
MAX(%(alias)s.created_ts) as CREATED_TS
FROM %(name)s as %(alias)s, agent as ag
WHERE %(alias)s.created_ts < '%(date)s'
AND ag.code = %(alias)s.agent_id
AND %(alias)s.agent_id NOT IN (
    SELECT DISTINCT %(alias)s.agent_id
    FROM %(name)s as %(alias)s
    WHERE created_ts >= '%(date)s')
GROUP BY ag.dp_code""" % {'alias': alias,
                                          'name': self.name,
                                          'date': compliance_date}

        return sql

    def reference_exception_sql(self, alias='st'):
        """Items in ``agent_stocktake`` table not found Toll Parcel Portal.

        **Kwargs:**
            *alias*: table alias (default ``st``)

        **Returns:**
            the SQL string

        """
        sql = """SELECT DISTINCT %(alias)s.id as AG_ID,
       %(alias)s.agent_id as AGENT_CODE,
       %(alias)s.reference_nbr REFERENCE_NBR,
       (SELECT ag.dp_code
        FROM agent as ag
        WHERE ag.code = %(alias)s.agent_id) as DP_CODE,
       (SELECT ag.name
        FROM agent as ag
        WHERE ag.code = %(alias)s.agent_id) as AGENT_NAME
FROM %(name)s as %(alias)s, agent as ag
WHERE %(alias)s.reference_nbr NOT IN
(SELECT ji.connote_nbr
 FROM job_item as ji)
AND %(alias)s.reference_nbr NOT IN
(SELECT ji.item_nbr
 FROM job_item as ji)
AND %(alias)s.reference_nbr NOT IN
(SELECT j.card_ref_nbr
 FROM job as j, job_item as ji
 WHERE ji.job_id = j.id)""" % {'name': self.name,
                               'alias': alias}

        return sql
