__all__ = [
    "JobItem",
]
import datetime

import nparcel


class JobItem(nparcel.Table):
    """Nparcel DB Job_Item table ORM.
    """
    _job = nparcel.Job()

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

    def uncollected_jobitems_sql(self, service_code=3, bu_ids=None):
        """SQL wrapper to extract uncollected Service Code-based jobs.

        Service Code jobs are identified by a integer value in the
        ``job.service_code`` column.

        Query will ignore records that have either white space or
        a spurious ``.`` in the email or phone number columns.

        The *bu_ids* relate to the ``job.bu_id`` column.

        **Args:**
            *service_code*: value relating to the ``job.service_code``
            column (default ``3`` for Primary Elect)

            *bu_ids*: integer based tuple of Business Unit ID's to search
            against (default ``None`` ignores all Business Units)

        **Returns:**
            the SQL string

        """
        if bu_ids is None:
            bu_ids = tuple()

        sql = """SELECT ji.id, ji.connote_nbr, ji.item_nbr
FROM job as j, %s as ji
WHERE ji.job_id = j.id
AND ji.pickup_ts is NULL
AND ji.notify_ts is NULL
AND (ji.email_addr NOT IN ('', '.') OR ji.phone_nbr NOT IN ('', '.'))
AND j.bu_id IN %s
AND j.service_code = %d""" % (self.name, str(bu_ids), service_code)

        return sql

    def reference_sql(self, reference_nbr):
        """Extract connote_nbr/item_nbr against *reference_nbr*.

        Query is an ``OR`` against both ``connote_nbr`` and ``item_nbr``.

        **Args:**
            *reference_nbr*: parcel ID number as scanned by the agent

        **Returns:**
            the SQL string

        """
        sql = """SELECT ji.id, ji.connote_nbr, ji.item_nbr
FROM %(name)s as ji
WHERE ji.connote_nbr = '%(ref)s'
OR ji.item_nbr = '%(ref)s'""" % {'name': self.name, 'ref': reference_nbr}

        return sql

    def job_based_reference_sql(self, reference_nbr, db_alias='ji'):
        """Extract connote_nbr/item_nbr against *reference_nbr* matched
        to the ``job.card_ref_nbr``.

        Query is an ``OR`` against both ``connote_nbr`` and ``item_nbr``.

        **Args:**
            *reference_nbr*: parcel ID number as scanned by the agent

        **Kwargs:**
            *db_string*: table alias

        **Returns:**
            the SQL string

        """
        sql = """SELECT %(alias)s.id,
       %(alias)s.connote_nbr,
       %(alias)s.item_nbr
FROM %(name)s as %(alias)s
WHERE %(alias)s.job_id IN
(
%(sql)s
)""" % {'name': self.name,
        'sql': self._job.reference_sql(reference_nbr),
        'alias': db_alias}

        return sql
