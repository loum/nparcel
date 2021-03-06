__all__ = [
    "JobItem",
]
import datetime

import top


class JobItem(top.Table):
    """job_item table ORM.
    """
    _job = top.Job()
    _agent_stocktake = top.AgentStocktake()

    def __init__(self):
        """Toll Outlet Portal job_item table initialiser.
        """
        super(JobItem, self).__init__('job_item')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "job_id INTEGER",
                "connote_nbr CHAR(30)",
                "item_nbr CHAR(32)",
                "consumer_name CHAR(30)",
                "email_addr CHAR(60)",
                "phone_nbr CHAR(20)",
                "pieces INTEGER",
                "status INTEGER",
                "created_ts TIMESTAMP",
                "pickup_ts TIMESTAMP",
                "pod_name CHAR(40)",
                "identity_type_id INTEGER",
                "identity_type_data CHAR(30)",
                "extract_ts TIMESTAMP",
                "reminder_ts TIMESTAMP",
                "notify_ts TIMESTAMP"]

    def collected_sql(self, business_unit, ignore_pe=False):
        """SQL wrapper to extract the collected items from the "jobitems"
        table.

        **Args:**
            *business_unit*: the id relating to the job.bu_id value.

        **Kwargs:**
            *ignore_pe*: ``boolean`` flag to ignore job items whose
            parent job is Primary Elect (default ``False``)

        **Returns:**
            the SQL string

        """
        sql = """SELECT ji.connote_nbr as 'REF1',
    ji.id as 'JOB_KEY',
    ji.pickup_ts as 'PICKUP_TIME',
    ji.pod_name as 'PICKUP_POD',
    it.description as 'IDENTITY_TYPE',
    ji.identity_type_data as 'IDENTITY_DATA',
    ji.item_nbr as 'ITEM_NBR',
    ag.code as 'AGENT_ID',
    ag.state as 'AGENT_STATE'
FROM job_item as ji, identity_type as it, job as j, agent as ag
WHERE pickup_ts IS NOT null
AND extract_ts IS null
AND ji.identity_type_id = it.id
AND j.agent_id = ag.id
AND (ji.job_id = j.id AND j.bu_id = %d)""" % business_unit

        if ignore_pe:
            sql += """
AND (j.service_code != 3 OR j.service_code IS NULL)"""

        return sql

    def upd_collected_sql(self, id, time):
        """SQL wrapper to update the collected items from the "jobitems"
        table.

        **Args:**
            *id*: the id relating to the ``jobitem.id`` value.

        **Returns:**
            the SQL string

        """
        sql = """UPDATE job_item
SET extract_ts = '%s'
WHERE id = %d""" % (time, id)

        return sql

    def upd_file_based_collected_sql(self, connote, item_nbr, time=None):
        """SQL wrapper to update the collected items from the "jobitems"
        table.

        This variant of the :meth:`upd_collected_sql` method is used
        to close of file-based extractions.

        **Args:**
            *connote*: connote value relating to the ``jobitem.connote_nbr``
            value

            *item_nbr*: connote value relating to the ``jobitem.item_nbr``
            value

        **Kwargs:**
            *time*: override the time to set from the current time

        **Returns:**
            the SQL string

        """
        if time is None:
            time = datetime.datetime.now().isoformat(' ').split('.', 1)[0]

        sql = """UPDATE %(name)s
SET extract_ts = '%(time)s', pickup_ts = '%(time)s'
WHERE connote_nbr = '%(connote)s'
AND item_nbr = '%(item_nbr)s'""" % {'name': self.name,
                                    'time': time,
                                    'connote': connote,
                                    'item_nbr': item_nbr}

        return sql

    def connote_sql(self, connote):
        """SQL wrapper to extract records where job_item.connote_nbr
        is equal to *connote*.

        **Args:**
            connote: Connote value relating to the job_item.connote_nbr
            column.

        **Returns:**
            the SQL string

        """
        sql = """SELECT id
FROM %s
WHERE connote_nbr = '%s'""" % (self.name, connote)

        return sql

    def connote_item_nbr_sql(self, connote, item_nbr):
        """SQL wrapper to extract records where job_item.connote_nbr
        is equal to *connote* and job_item.item_nbr equals *item_nbr*.

        **Args:**
            connote: Connote value relating to the job_item.connote_nbr
            column.

            item_nbr: Item Number value relating to the job_item.item_nbr
            column.

        **Returns:**
            the SQL string

        """
        sql = """SELECT id
FROM %s
WHERE connote_nbr = '%s'
AND item_nbr = '%s'
ORDER BY created_ts DESC""" % (self.name, connote, item_nbr)

        return sql

    def item_number_sql(self, item_nbr):
        """SQL wrapper to extract records where job_item.item_nbr
        is equal to *item_nbr*.

        **Args:**
            item_nbr: Item Number value relating to the job_item.item_nbr
            column.

        **Returns:**
            the SQL string

        """
        sql = """SELECT id
FROM %s
WHERE item_nbr = '%s'""" % (self.name, item_nbr)

        return sql

    def uncollected_sql(self, start_date, uncollected_period):
        """SQL wrapper to extract the job_item records which remain
        uncollected after *uncollected_period* has elapsed.

        **Args:**
            uncollected_period: job_item.notify_ts value that defines
            an uncollected parcel

        **Returns:**
            the SQL string

        """
        sql = """SELECT id
FROM job_item
WHERE (created_ts > '%s' AND notify_ts < '%s')
AND pickup_ts IS NULL
AND (email_addr != '' OR phone_nbr != '')
AND reminder_ts IS NULL""" % (start_date, uncollected_period)

        return sql

    def job_item_agent_details_sql(self, job_item_id):
        """SQL wrapper to extract the agent details against a *job_item_id*.

        SQL also returns additional information relating to the
        *job_item_id* such as:

        * ``jobitem.connote_nbr``
        * ``jobitem.item_nbr``
        * ``jobitem.notify_ts``
        * ``jobitem.created_ts``
        * ``jobitem.email_addr``
        * ``jobitem.phone_nbr``
        * ``jobitem.pickup_ts``

        and the *job.bu_id*.

        **Args:**
            job_item_id: the jobitem.id value to search against

        **Returns:**
            the SQL string

        """
        sql = """SELECT ag.name,
       ag.address,
       ag.suburb,
       ag.postcode,
       ji.connote_nbr,
       ji.item_nbr,
       ji.notify_ts,
       ji.created_ts,
       ji.email_addr,
       ji.phone_nbr,
       ji.pickup_ts,
       j.bu_id
FROM job_item as ji, job as j, agent as ag
WHERE ji.job_id = j.id
AND j.agent_id = ag.id
AND ji.id = %d""" % job_item_id

        return sql

    def update_reminder_ts_sql(self, id, ts=None):
        return self.update_timestamp_sql(id, column='reminder_ts', ts=ts)

    def update_notify_ts_sql(self, id, ts=None):
        return self.update_timestamp_sql(id, column='notify_ts', ts=ts)

    def update_timestamp_sql(self, id, column, ts=None):
        """SQL wrapper to update the ``job_item.reminder_ts`` to *ts*
        timestamp.

        **Args:**
            *id*: integer value relating to the ``job_item.id``

            *column*: the timestamp column to update

        **Kwargs:**
            *ts*: override the current time

        **Returns:**
            the SQL string

        """
        if ts is None:
            ts = datetime.datetime.now().isoformat(' ').split('.', 1)[0]

        sql = """UPDATE %s
SET %s = '%s'
WHERE id = %d
""" % (self.name, column, ts, id)

        return sql

    def connote_base_primary_elect_job(self, connote):
        """SQL wrapper to verify if a *connote* is associated with a primary
        elect job.

        Primary elect jobs are identified by a integer value 3 in the
        ``job.service_code`` column.

        **Args:**
            connote: the jobitem.connote value to search against.

        **Returns:**
            the SQL string

        """
        sql = """SELECT ji.id
FROM job as j, %s as ji
WHERE ji.job_id = j.id
AND ji.connote_nbr = '%s'
AND ji.notify_ts IS NULL
AND (ji.email_addr != '' OR ji.phone_nbr != '')
AND j.service_code = 3""" % (self.name, connote)

        return sql

    def uncollected_jobitems_sql(self,
                                 service_code=3,
                                 bu_ids=None,
                                 delivery_partners=None,
                                 day_range=14):
        """SQL wrapper to extract uncollected Service Code-based jobs.

        Service Code jobs are identified by a integer value in the
        ``job.service_code`` column.

        Query will ignore records that have either white space or
        a spurious ``.`` in the email or phone number columns.

        The *bu_ids* relate to the ``job.bu_id`` column.

        **Kwargs:**
            *service_code*: value relating to the ``job.service_code``
            column (default ``3`` for Primary Elect)

            *bu_ids*: integer based tuple of Business Unit ID's to search
            against (default ``None`` ignores all Business Units)

            *day_range*: number of days from current time to include
            in search (default 14.0 days)

        **Returns:**
            the SQL string

        """
        if bu_ids is None:
            bu_ids = tuple()
        if len(bu_ids) == 1:
            bu_ids = '(%d)' % bu_ids[0]

        if delivery_partners is None:
            delivery_partners = tuple()
        if len(delivery_partners) == 1:
            delivery_partners = "('%s')" % delivery_partners[0]

        now = datetime.datetime.now()
        start_ts = now - datetime.timedelta(days=day_range)
        start_date = start_ts.strftime('%Y-%m-%d %H:%M:%S')

        sql = """SELECT ji.id, ji.connote_nbr, ji.item_nbr
FROM job AS j, %(name)s AS ji, agent AS ag, delivery_partner AS dp
WHERE ji.job_id = j.id
AND j.agent_id = ag.id
AND ag.dp_id = dp.id
AND dp.name IN %(dps)s
AND ji.pickup_ts IS NULL
AND ji.notify_ts IS NULL
AND (ji.email_addr NOT IN ('', '.') OR ji.phone_nbr NOT IN ('', '.'))
AND j.bu_id IN %(bu_ids)s
AND j.service_code = %(sc)d
AND ji.created_ts > '%(start_date)s'""" % {'name': self.name,
                                           'dps': str(delivery_partners),
                                           'bu_ids': str(bu_ids),
                                           'sc': service_code,
                                           'start_date': start_date}

        return sql

    def reference_sql(self,
                      bu_ids,
                      reference_nbr=None,
                      picked_up=False,
                      delivery_partners=None,
                      columns=None,
                      alias='ji'):
        """Extract connote_nbr/item_nbr against *reference_nbr*.

        Query is an ``OR`` against both ``connote_nbr`` and ``item_nbr``.

        **Args:**
            *bu_ids*: integer based tuple of Business Unit ID's to search
            against (default ``None`` ignores all Business Units)

        **Kwargs:**
            *reference_nbr*: parcel ID number as scanned by the agent.  If
            ``None``, then the values from the ``agent_stocktake`` table
            will be used.

            *picked_up*: boolean flag that will extract ``job_items``
            that have been picked up if ``True``. Otherwise, will extract
            ``job_items`` that have not been picked up if ``False``.

            *delivery_partners*: string based list of Delivery Partner
            names to limit result set against.  For example,
            ``['Nparcel', 'Toll']``.  The values supported are as per
            the ``delivery_partner.name`` table set

            *columns*: string prepresentation of the columns to query
            against

            *alias*: table alias (default ``ji``)

        **Returns:**
            the SQL string

        """
        if columns is None:
            columns = self._select_columns(alias)

        if not picked_up:
            pickup_sql = 'IS NULL'
        else:
            pickup_sql = 'IS NOT NULL'

        if len(bu_ids) == 1:
            bu_ids = '(%d)' % bu_ids[0]

        ref = reference_nbr
        if reference_nbr is None:
            ref = self._agent_stocktake.reference_sql()

        dp_sql = str()
        if delivery_partners is not None:
            dps = ', '.join(["'%s'" % x for x in delivery_partners])
            dps = '(%s)' % dps
            if len(delivery_partners) == 1:
                dps = "('%s')" % delivery_partners[0]

            dp_sql = """AND dp.name IN %s AND ag.dp_id = dp.id""" % dps

        union_sql = self.job_based_reference_sql(bu_ids,
                                                 ref,
                                                 picked_up,
                                                 delivery_partners,
                                                 columns)

        sql = """SELECT DISTINCT %(columns)s
FROM %(name)s as %(alias)s,
     job AS j,
     agent AS ag,
     agent_stocktake AS st,
     delivery_partner AS dp
WHERE %(alias)s.job_id = j.id
AND ag.id = st.agent_id
AND j.bu_id IN %(bu_ids)s
AND j.agent_id = ag.id
AND (%(alias)s.connote_nbr IN (%(ref)s)
     OR %(alias)s.item_nbr IN (%(ref)s))
AND %(alias)s.pickup_ts %(pickup_sql)s
%(dp_sql)s
UNION
%(union)s""" % {'columns': columns,
                'bu_ids': str(bu_ids),
                'name': self.name,
                'ref': ref,
                'alias': alias,
                'union': union_sql,
                'pickup_sql': pickup_sql,
                'dp_sql': dp_sql}

        return sql

    def job_based_reference_sql(self,
                                bu_ids,
                                reference_nbr,
                                picked_up=False,
                                delivery_partners=None,
                                columns=None,
                                alias='ji'):
        """Extract connote_nbr/item_nbr against *reference_nbr* matched
        to the ``job.card_ref_nbr``.

        Query is an ``OR`` against both ``connote_nbr`` and ``item_nbr``.

        **Args:**
            *bu_ids*: integer based tuple of Business Unit ID's to search
            against (default ``None`` ignores all Business Units)

            *reference_nbr*: parcel ID number as scanned by the agent

        **Kwargs:**
            *picked_up*: boolean flag that will extract ``job_items``
            that have been picked up if ``True``. Otherwise, will extract
            ``job_items`` that have not been picked up if ``False``.

            *delivery_partners*: string based list of Delivery Partner
            names to limit result set against.  For example,
            ``['Nparcel', 'Toll']``.  The values supported are as per
            the ``delivery_partner.name`` table set

            *columns*: string prepresentation of the columns to query
            against

            *alias*: table alias

        **Returns:**
            the SQL string

        """
        if columns is None:
            columns = self._select_columns(alias)

        pickup_sql = 'AND %s.pickup_ts ' % alias
        if not picked_up:
            pickup_sql += 'IS NULL'
        else:
            pickup_sql += 'IS NOT NULL'

        if len(bu_ids) == 1:
            bu_ids = '(%d)' % bu_ids[0]

        dp_sql = str()
        if delivery_partners is not None:
            dps = ', '.join(["'%s'" % x for x in delivery_partners])
            dps = '(%s)' % dps
            if len(delivery_partners):
                dps = "('%s')" % delivery_partners[0]

            dp_sql = """AND dp.name IN %s AND ag.dp_id = dp.id""" % dps

        sql = """SELECT DISTINCT %(columns)s
FROM %(name)s AS %(alias)s,
     job AS j,
     agent AS ag,
     delivery_partner AS dp,
     agent_stocktake AS st
WHERE %(alias)s.job_id = j.id
AND j.bu_id IN %(bu_ids)s
AND j.agent_id = ag.id
%(dp_sql)s
AND %(alias)s.job_id IN
(
%(sql)s
)
%(pickup_sql)s""" % {'columns': columns,
                     'bu_ids': bu_ids,
                     'name': self.name,
                     'sql': self._job.reference_sql(reference_nbr),
                     'alias': alias,
                     'pickup_sql': pickup_sql,
                     'dp_sql': dp_sql}

        return sql

    def _select_columns(self, alias='ji'):
        """Helper method that captures required columns in the
        uncollected aged report query.

        **Kwargs:**
            *alias*: table alias

        **Returns:**
            the SQL string

        """
        columns = """%(alias)s.id as JOB_ITEM_ID,
       j.bu_id as JOB_BU_ID,
       %(alias)s.connote_nbr as CONNOTE_NBR,
       j.card_ref_nbr as BARCODE,
       %(alias)s.item_nbr as ITEM_NBR,
       j.job_ts as JOB_TS,
       %(alias)s.created_ts as CREATED_TS,
       %(alias)s.notify_ts as NOTIFY_TS,
       %(alias)s.pickup_ts as PICKUP_TS,
       %(alias)s.pieces as PIECES,
       %(alias)s.consumer_name as CONSUMER_NAME,
       ag.dp_code as DP_CODE,
       ag.code as AGENT_CODE,
       ag.name as AGENT_NAME,
       ag.address as AGENT_ADDRESS,
       ag.suburb as AGENT_SUBURB,
       ag.state as AGENT_STATE,
       ag.postcode as AGENT_POSTCODE,
       ag.phone_nbr as AGENT_PHONE_NBR,
       (SELECT DISTINCT ag.dp_code
        FROM agent_stocktake AS st, agent AS aag
        WHERE (%(alias)s.connote_nbr = st.reference_nbr
               OR j.card_ref_nbr = st.reference_nbr
               OR %(alias)s.item_nbr = st.reference_nbr)
        AND st.agent_id = aag.id) AS ST_DP_CODE,
       (SELECT DISTINCT ag.code
        FROM agent_stocktake AS st, agent AS aag
        WHERE (%(alias)s.connote_nbr = st.reference_nbr
               OR j.card_ref_nbr = st.reference_nbr
               OR %(alias)s.item_nbr = st.reference_nbr)
        AND st.agent_id = aag.id) AS ST_AGENT_CODE,
       (SELECT DISTINCT ag.name
        FROM agent_stocktake AS st, agent AS aag
        WHERE (%(alias)s.connote_nbr = st.reference_nbr
               OR j.card_ref_nbr = st.reference_nbr
               OR %(alias)s.item_nbr = st.reference_nbr)
        AND st.agent_id = aag.id) AS ST_AGENT_NAME""" % {'alias': alias}

        return columns

    def non_compliance_sql(self,
                           bu_ids,
                           picked_up=False,
                           delivery_partners=None,
                           alias='ji'):
        """Extract ``job_item`` detail of all items in the ``job_item``
        table that do not exist in the ``agent_stocktake`` table.

        Senarios are based on the *picked_up* flag.  For example, all
        parcels that *have* been picked up or *have not* been picked up.

        **Args:**
            *bu_ids*: integer based tuple of Business Unit ID's to search
            against (default ``None`` ignores all Business Units)

        **Kwargs:**
            *picked_up*: boolean flag that will extract ``job_items``
            that have been picked up if ``True``. Otherwise, will extract
            ``job_items`` that have not been picked up if ``False``.

            *delivery_partners*: string based list of Delivery Partner
            names to limit result set against.  For example,
            ``['Nparcel', 'Toll']``.  The values supported are as per
            the ``delivery_partner.name`` table set

            *alias*: table alias (default ``ji``)

        **Returns:**
            the SQL string

        """
        if bu_ids is None:
            bu_ids = tuple()

        if len(bu_ids) == 1:
            bu_ids = '(%d)' % bu_ids[0]

        columns = self._select_columns(alias)
        col = 'ji.id'

        if not picked_up:
            pickup_sql = 'IS NULL'
        else:
            pickup_sql = 'IS NOT NULL'

        dp_sql = str()
        if delivery_partners is not None:
            dps = ', '.join(["'%s'" % x for x in delivery_partners])
            dps = '(%s)' % dps
            if len(delivery_partners) == 1:
                dps = "('%s')" % delivery_partners[0]

            dp_sql = """AND dp.name IN %s AND ag.dp_id = dp.id""" % dps

        sql = """SELECT DISTINCT %(columns)s
FROM %(name)s AS %(alias)s, job AS j, agent AS ag, delivery_partner AS dp
WHERE %(alias)s.job_id = j.id
AND j.agent_id = ag.id
AND %(alias)s.pickup_ts %(pickup_sql)s
%(dp_sql)s
AND ji.id NOT IN
(%(sql)s)""" % {'columns': columns,
                'alias': alias,
                'name': self.name,
                'pickup_sql': pickup_sql,
                'dp_sql': dp_sql,
                'sql': self.reference_sql(bu_ids=bu_ids,
                                          picked_up=picked_up,
                                          delivery_partners=delivery_partners,
                                          columns=col)}

        return sql

    def total_agent_stocktake_parcel_count_sql(self,
                                               bu_ids,
                                               picked_up=False,
                                               delivery_partners=None,
                                               day_range=7,
                                               alias='ji'):
        """Sum ``agent_stocktake`` based parcel counts per ADP based on
        *picked_up*.

        Query is an ``OR`` against both ``connote_nbr`` and ``item_nbr``.

        **Args:**
            *bu_ids*: integer based tuple of Business Unit ID's to search
            against (default ``None`` ignores all Business Units)

        **Kwargs:**
            *picked_up*: boolean flag that will extract ``job_items``
            that have been picked up if ``True``. Otherwise, will extract
            ``job_items`` that have not been picked up if ``False``.

            *delivery_partners*: string based tuple of Delivery Partner
            names to limit result set against.  For example,
            ``['top', 'toll']``.  The values supported are as per
            the ``delivery_partner.name`` table set

            *day_range*: number of days from current time to include
            in the agent_stocktake table search (default 7 days)

            *alias*: table alias (default ``ji``)

        **Returns:**
            the SQL string

        """
        now = datetime.datetime.now()
        start_ts = now - datetime.timedelta(days=day_range)
        start_date = start_ts.strftime('%Y-%m-%d %H:%M:%S')

        if not picked_up:
            pickup_sql = 'IS NULL'
        else:
            pickup_sql = 'IS NOT NULL'

        if len(bu_ids) == 1:
            bu_ids = '(%d)' % bu_ids[0]

        col = 'st.reference_nbr'
        sql_ref = self.reference_sql(bu_ids=bu_ids,
                                     picked_up=picked_up,
                                     delivery_partners=delivery_partners,
                                     columns=col)

        sql = """SELECT DISTINCT agent.dp_code AS DP_CODE,
        agent.code AS AGENT_CODE,
        agent.name AS AGENT_NAME,
        (SELECT MAX(st.created_ts)
         FROM agent_stocktake AS st, agent AS ag
         WHERE ag.code = agent.code
         AND ag.id = st.agent_id) AS STOCKTAKE_CREATED_TS,
        (SELECT COUNT(DISTINCT ags.reference_nbr)
         FROM agent_stocktake AS ags, agent AS ag
         WHERE ags.agent_id = agent.id
         AND ags.created_ts > '%(start_date)s') AS AGENT_PIECES,
        (SELECT COUNT(ji.id)
         FROM job_item AS ji, job AS j, agent AS ag
         WHERE ag.id = agent.id
         AND j.agent_id = ag.id
         AND j.id = ji.job_id
         AND ji.pickup_ts %(pickup_sql)s) AS TPP_PIECES
FROM agent AS agent, agent_stocktake AS agent_stocktake
WHERE agent_stocktake.agent_id = agent.id
AND reference_nbr != ''
AND agent_stocktake.created_ts > '%(start_date)s'
AND agent_stocktake.reference_nbr IN (%(sql_ref)s)
GROUP BY agent.id,
         agent.dp_code,
         agent.code,
         agent.name,
         agent_stocktake.created_ts,
         agent_stocktake.reference_nbr""" % {'sql_ref': sql_ref,
                                             'start_date': start_date,
                                             'pickup_sql': pickup_sql}

        return sql

    def total_parcel_count_sql(self,
                               picked_up=False,
                               delivery_partners=None,
                               alias='ji'):
        """Sum parcel counts per ADP based on *picked_up*.

        **Kwargs:**
            *picked_up*: boolean flag that will extract ``job_items``
            that have been picked up if ``True``. Otherwise, will extract
            ``job_items`` that have not been picked up if ``False``.

            *delivery_partners*: string based tuple of Delivery Partner
            names to limit result set against.  For example,
            ``['Nparcel', 'Toll']``.  The values supported are as per
            the ``delivery_partner.name`` table set

            *alias*: table alias (default ``ji``)

        **Returns:**
            the SQL string

        """
        if not picked_up:
            pickup_sql = 'IS NULL'
        else:
            pickup_sql = 'IS NOT NULL'

        dp_sql = str()
        if delivery_partners is not None:
            dps = ', '.join(["'%s'" % x for x in delivery_partners])
            dps = '(%s)' % dps
            if len(delivery_partners) == 1:
                dps = "('%s')" % delivery_partners[0]

            dp_sql = """AND dp.name IN %s AND ag.dp_id = dp.id""" % dps

        sql = """SELECT SUM(%(alias)s.pieces)
FROM %(name)s AS %(alias)s, job AS j, agent AS ag, delivery_partner AS dp
WHERE %(alias)s.job_id = j.id
AND j.agent_id = ag.id
%(dp_sql)s
AND %(alias)s.pickup_ts %(pickup_sql)s""" % {'name': self.name,
                                             'dp_sql': dp_sql,
                                             'pickup_sql': pickup_sql,
                                             'alias': alias}

        return sql

    def agent_id_of_aged_parcels(self,
                                 period=7,
                                 delivery_partners=None,
                                 alias='ji'):
        """SQL to provide a distinct list of agents that have an
        aged parcel.

        **Kwargs:**
            *period*: time (in days) from now that is the cut off for
            agent compliance (default 7 days)

            *delivery_partners*: string based tuple of Delivery Partner
            names to limit result set against.  For example,
            ``['top', 'toll']``.  The values supported are as per
            the ``delivery_partner.name`` table set

            *alias*: table alias (default ``ji``)

        **Returns:**
            the SQL string

        """
        now = datetime.datetime.now()
        ts = now - datetime.timedelta(days=period)
        date = ts.strftime('%Y-%m-%d %H:%M:%S')

        dps = delivery_partners
        kwargs = {'period': period,
                  'delivery_partners': dps}
        compliance_sql = self._agent_stocktake.compliance_sql(**kwargs)

        sql = """%(compliance_sql)s
AND ag.id IN
(SELECT DISTINCT(j.agent_id)
 FROM job as j, %(name)s AS %(alias)s, agent AS ag
 WHERE %(alias)s.job_id = j.id
 AND %(alias)s.created_ts < '%(date)s'
 AND %(alias)s.pickup_ts IS NULL)""" % {'compliance_sql': compliance_sql,
                                        'name': self.name,
                                        'alias': alias,
                                        'date': date}

        return sql
