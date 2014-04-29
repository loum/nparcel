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
FROM %(name)s AS %(alias)s
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

    def compliance_sql(self, period=7, delivery_partners=None, alias='st'):
        """Select agent information of agents that have not performed
        a stocktake since *period* days prior.

        **Kwargs:**
            *period*: time (in days) from now that is the cut off for
            agent compliance (default 7 days)

            *delivery_partners*: string based list of Delivery Partner
            names to limit result set against.  For example,
            ``['Nparcel', 'Toll']``.  The values supported are as per
            the ``delivery_partner.name`` table set

            *alias*: table alias (default ``st``)

        **Returns:**
            the SQL string

        """
        now = datetime.datetime.now()
        compliance_ts = now - datetime.timedelta(days=period)
        compliance_date = compliance_ts.strftime('%Y-%m-%d %H:%M:%S')

        dp_sql = str()
        if delivery_partners is not None:
            dps = ', '.join(["'%s'" % x for x in delivery_partners])
            dps = '(%s)' % dps
            if len(delivery_partners) == 1:
                dps = "('%s')" % delivery_partners[0]

            dp_sql = """AND dp.name IN %s AND ag.dp_id = dp.id""" % dps

        sql = """SELECT DISTINCT ag.dp_code AS DP_CODE,
       ag.code AS AGENT_CODE,
       ag.name AS AGENT_NAME,
       (SELECT MAX(st.created_ts)
        FROM agent_stocktake AS st
        WHERE st.agent_id = ag.id) AS CREATED_TS
FROM agent AS ag, delivery_partner AS dp
WHERE ag.id NOT IN
(SELECT st.agent_id
 FROM agent_stocktake AS st
 WHERE st.created_ts > '%(date)s')
%(dp_sql)s""" % {'date': compliance_date,
                 'dp_sql': dp_sql}

        return sql

    def reference_exception_sql(self,
                                day_range=7,
                                delivery_partners=None,
                                alias='st'):
        """Items in ``agent_stocktake`` table not found Toll Parcel Portal.

        **Kwargs:**
            *day_range*: number of days from current time to include
            in search (default 7.0 days)

            *delivery_partners*: string based tuple of Delivery Partner
            names to limit result set against.  For example,
            ``['Nparcel', 'Toll']``.  The values supported are as per
            the ``delivery_partner.name`` table set

            *alias*: table alias (default ``st``)

        **Returns:**
            the SQL string

        """
        now = datetime.datetime.now()
        start_ts = now - datetime.timedelta(days=day_range)
        start_date = start_ts.strftime('%Y-%m-%d %H:%M:%S')

        dp_sql = str()
        if delivery_partners is not None:
            dps = ', '.join(["'%s'" % x for x in delivery_partners])
            dps = '(%s)' % dps
            if len(delivery_partners) == 1:
                dps = "('%s')" % delivery_partners[0]

            dp_sql = """AND dp.name IN %s AND ag.dp_id = dp.id""" % dps

        sql = """SELECT DISTINCT %(alias)s.id AS AG_ID,
       ag.code AS AGENT_CODE,
       %(alias)s.reference_nbr AS REFERENCE_NBR,
       ag.dp_code AS DP_CODE,
       ag.name AS AGENT_NAME
FROM %(name)s AS %(alias)s, agent AS ag, delivery_partner AS dp
WHERE  ag.id = %(alias)s.agent_id
AND %(alias)s.created_ts > '%(start_date)s'
AND %(alias)s.reference_nbr NOT IN
(SELECT ji.connote_nbr
 FROM job_item AS ji)
AND %(alias)s.reference_nbr NOT IN
(SELECT ji.item_nbr
 FROM job_item AS ji)
AND %(alias)s.reference_nbr NOT IN
(SELECT j.card_ref_nbr
 FROM job AS j, job_item AS ji
 WHERE ji.job_id = j.id)
%(dp_sql)s""" % {'name': self.name,
                 'alias': alias,
                 'start_date': start_date,
                 'dp_sql': dp_sql}

        return sql

    def stocktake_created_date(self, *args):
        """Return the most current ``agent_stocktake.created_ts`` of an
        agent_stocktake record against ``agent_stocktake.reference_nbr``
        on either *connote_nbr*, *barcode* or item_nbr.

        **Args:**
            *args*: list of search keys to use against the
            ``agent_stocktake.reference_nbr`` column.  Typcially, these
            are the ``job_item.connote_nbr``, ``job.barcode`` and
            ``job_item.item_nbr``.

        **Returns:**
            the SQL string

        """
        if len(args) == 1:
            refs = "('%s')" % args[0]
        else:
            refs = tuple('%s' % x for x in args)

        sql = """SELECT MAX(created_ts)
FROM %(name)s
WHERE reference_nbr IN %(refs)s""" % {'name': self.name, 'refs': refs}

        return sql
