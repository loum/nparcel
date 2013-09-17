__all__ = [
    "JobItem",
]
import nparcel


class JobItem(nparcel.Table):
    """Nparcel DB Job_Item table ORM.
    """

    def __init__(self):
        """
        """
        self._name = 'job_item'
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
                "reminder_ts TIMESTAMP"]

    def collected_sql(self, business_unit):
        """SQL wrapper to extract the collected items from the "jobitems"
        table.

        **Args:**
            business_unit: the id relating to the job.bu_id value.

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
WHERE connote_nbr = '%s'""" % (self._name, connote)

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
AND item_nbr = '%s'""" % (self._name, connote, item_nbr)

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
WHERE item_nbr = '%s'""" % (self._name, item_nbr)

        return sql

    def uncollected_sql(self, start_date, uncollected_period):
        """SQL wrapper to extract the job_item records which remain
        uncollected after *uncollected_period* has elapsed.

        **Args:**
            uncollected_period: job_item.created_ts value that defines
            an uncollected parcel

        **Returns:**
            the SQL string

        """
        sql = """SELECT id
FROM job_item
WHERE (created_ts > '%s' AND created_ts < '%s')
AND pickup_ts IS NULL
AND reminder_ts IS NULL""" % (start_date, uncollected_period)

        return sql
