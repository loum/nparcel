__all__ = [
    "JobItem",
]
import datetime

import nparcel


class JobItem(nparcel.Table):
    """Nparcel DB Job_Item table ORM.
    """
    _job = nparcel.Job()
    _agent_stocktake = nparcel.AgentStocktake()

    def __init__(self):
        """Nparcel job_item table initialiser.
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

    def upd_collected_sql(self, business_unit, time):
        """SQL wrapper to update the collected items from the "jobitems"
        table.

        **Args:**
            business_unit: the id relating to the job.bu_id value.

        **Returns:**
            the SQL string

        """
        sql = """UPDATE job_item
SET extract_ts = '%s'
WHERE id = %d
""" % (time, business_unit)

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
AND item_nbr = '%s'""" % (self.name, connote, item_nbr)

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
        * ``jobitem.create_ts``
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
            ts = datetime.datetime.now().isoformat(' ')[:-3]

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

        now = datetime.datetime.now()
        start_ts = now - datetime.timedelta(days=day_range)
        start_date = start_ts.strftime('%Y-%m-%d %H:%M:%S')

        sql = """SELECT ji.id, ji.connote_nbr, ji.item_nbr
FROM job as j, %s as ji
WHERE ji.job_id = j.id
AND ji.pickup_ts is NULL
AND ji.notify_ts is NULL
AND (ji.email_addr NOT IN ('', '.') OR ji.phone_nbr NOT IN ('', '.'))
AND j.bu_id IN %s
AND j.service_code = %d
AND ji.created_ts > '%s'""" % (self.name,
                               str(bu_ids),
                               service_code,
                               start_date)

        return sql

    def reference_sql(self,
                      bu_ids,
                      reference_nbr=None,
                      picked_up=False,
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

        sql = """SELECT DISTINCT %(columns)s
FROM %(name)s as %(alias)s, job as j, agent as ag, agent_stocktake as st
WHERE %(alias)s.job_id = j.id
AND ag.id = st.agent_id
AND j.bu_id IN %(bu_ids)s
AND j.agent_id = ag.id
AND (%(alias)s.connote_nbr IN (%(ref)s)
     OR %(alias)s.item_nbr IN (%(ref)s))
AND %(alias)s.pickup_ts %(pickup_sql)s
UNION
%(union)s""" % {'columns': columns,
                'bu_ids': str(bu_ids),
                'name': self.name,
                'ref': ref,
                'alias': alias,
                'union': self.job_based_reference_sql(bu_ids=bu_ids,
                                                      reference_nbr=ref,
                                                      picked_up=picked_up,
                                                      columns=columns),
                'pickup_sql': pickup_sql}

        return sql

    def job_based_reference_sql(self,
                                bu_ids,
                                reference_nbr,
                                picked_up=False,
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

        sql = """SELECT DISTINCT %(columns)s
FROM %(name)s as %(alias)s, job as j, agent as ag
WHERE %(alias)s.job_id = j.id
AND j.bu_id IN %(bu_ids)s
AND j.agent_id = ag.id
AND %(alias)s.job_id IN
(
%(sql)s
)
%(pickup_sql)s""" % {'columns': columns,
                     'bu_ids': bu_ids,
                     'name': self.name,
                     'sql': self._job.reference_sql(reference_nbr),
                     'alias': alias,
                     'pickup_sql': pickup_sql}

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
       (SELECT ag.dp_code
        FROM agent_stocktake AS st, agent AS ag
        WHERE (%(alias)s.connote_nbr = st.reference_nbr
               OR j.card_ref_nbr = st.reference_nbr
               OR %(alias)s.item_nbr = st.reference_nbr)
        AND st.agent_id = ag.id) AS ST_DP_CODE,
       (SELECT ag.code
        FROM agent_stocktake AS st, agent AS ag
        WHERE (%(alias)s.connote_nbr = st.reference_nbr
               OR j.card_ref_nbr = st.reference_nbr
               OR %(alias)s.item_nbr = st.reference_nbr)
        AND st.agent_id = ag.id) AS ST_AGENT_CODE,
       (SELECT ag.name
        FROM agent_stocktake AS st, agent AS ag
        WHERE (%(alias)s.connote_nbr = st.reference_nbr
               OR j.card_ref_nbr = st.reference_nbr
               OR %(alias)s.item_nbr = st.reference_nbr)
        AND st.agent_id = ag.id) AS ST_AGENT_NAME""" % {'alias': alias}

        return columns

    def non_compliance_sql(self, bu_ids, picked_up=False, alias='ji'):
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

        sql = """SELECT %(columns)s
FROM %(name)s as %(alias)s, job as j, agent as ag
WHERE %(alias)s.job_id = j.id
AND j.agent_id = ag.id
AND %(alias)s.pickup_ts %(pickup_sql)s
AND ji.id NOT IN
(%(sql)s)""" % {'columns': columns,
                'alias': alias,
                'name': self.name,
                'pickup_sql': pickup_sql,
                'sql': self.reference_sql(bu_ids=bu_ids,
                                          picked_up=picked_up,
                                          columns=col)}

        return sql

    def total_agent_stocktake_parcel_count_sql(self,
                                               bu_ids,
                                               reference_nbr=None,
                                               picked_up=False,
                                               columns=None,
                                               alias='ji'):
        """Sum ``agent_stocktake`` based parcel counts per ADP based on
        *picked_up*.

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

        columns = """%(alias)s.pieces as PIECES,
       ag.dp_code as DP_CODE,
       ag.code as AGENT_CODE,
       ag.name as AGENT_NAME""" % {'alias': alias}

        sql = """SELECT DP_CODE,
       AGENT_CODE,
       AGENT_NAME,
       (SELECT MAX(st.created_ts)
        FROM agent_stocktake AS st, agent AS ag
        WHERE ag.code = AGENT_CODE
        AND ag.id = st.agent_id) AS STOCKTAKE_CREATED_TS,
       SUM(PIECES) AS AGENT_PIECES,
       (SELECT SUM(%(alias)s.pieces)
        FROM %(name)s as %(alias)s, job as j, agent as ag
        WHERE %(alias)s.job_id = j.id
        AND j.agent_id = ag.id
        AND ag.code = AGENT_CODE
        AND %(alias)s.pickup_ts %(pickup_sql)s) AS TPP_PIECES
FROM (SELECT %(columns)s
 FROM %(name)s as %(alias)s, job as j, agent as ag
 WHERE %(alias)s.job_id = j.id
 AND j.bu_id IN %(bu_ids)s
 AND j.agent_id = ag.id
 AND (%(alias)s.connote_nbr IN (%(ref)s)
      OR (%(alias)s.item_nbr IN (%(ref)s)))
 AND %(alias)s.pickup_ts %(pickup_sql)s
 UNION
 %(union)s) AS A
GROUP BY A.DP_CODE,
A.AGENT_NAME,
A.AGENT_CODE""" % {'columns': columns,
                   'bu_ids': str(bu_ids),
                   'name': self.name,
                   'ref': ref,
                   'alias': alias,
                   'union': self.job_based_reference_sql(bu_ids,
                                                         ref,
                                                         picked_up,
                                                         columns),
                   'job_item_count': self.total_parcel_count_sql(picked_up),
                   'pickup_sql': pickup_sql}

        return sql

    def total_parcel_count_sql(self, picked_up=False, alias='ji'):
        """Sum parcel counts per ADP based on *picked_up*.

        **Kwargs:**
            *picked_up*: boolean flag that will extract ``job_items``
            that have been picked up if ``True``. Otherwise, will extract
            ``job_items`` that have not been picked up if ``False``.

            *alias*: table alias (default ``ji``)

        **Returns:**
            the SQL string

        """
        if not picked_up:
            pickup_sql = 'IS NULL'
        else:
            pickup_sql = 'IS NOT NULL'

        sql = """SELECT SUM(%(alias)s.pieces)
FROM %(name)s as %(alias)s, job as j, agent as ag
WHERE %(alias)s.job_id = j.id
AND j.agent_id = ag.id
AND %(alias)s.pickup_ts %(pickup_sql)s""" % {'name': self.name,
                                             'pickup_sql': pickup_sql,
                                             'alias': alias}

        return sql

    def agent_id_of_aged_parcels(self, period=7, alias='ji'):
        """SQL to provide a distinct list of agents that have an
        aged parcel.

        **Kwargs:**
            *period*: time (in days) from now that is the cut off for
            agent compliance (default 7 days)

            *alias*: table alias (default ``ji``)

        **Returns:**
            the SQL string

        """
        now = datetime.datetime.now()
        ts = now - datetime.timedelta(days=period)
        date = ts.strftime('%Y-%m-%d %H:%M:%S')

        compliance_sql = self._agent_stocktake.compliance_sql(period=period)

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
