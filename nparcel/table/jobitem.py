__all__ = [
    "JobItem",
]
import datetime

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
                "consumer_name CHAR(30)",
                "pieces INTEGER",
                "status INTEGER",
                "created_ts TIMESTAMP",
                "pickup_ts TIMESTAMP",
                "pod_name CHAR(40)",
                "identity_type_id INTEGER",
                "identity_type_data CHAR(30)",
                "extract_ts TIMESTAMP"]

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
    ji.identity_type_data as 'IDENTITY_DATA'
FROM job_item as ji, identity_type as it, job as j
WHERE pickup_ts IS NOT null
AND extract_ts IS null
AND ji.identity_type_id = it.id
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

    def aged_sql(self, age):
        """SQL wrapper to return the items whose created_ts value
        breaches the *age* threshold.

        **Args:**
            age: time (in seconds) id relating to the job.bu_id value.

        **Returns:**
            the SQL string
        """
        now = datetime.datetime.now()
        aged_time = now - datetime.timedelta(seconds=age)
        sql = """SELECT *
FROM %s
WHERE created_ts < '%s'""" % (self._name, aged_time)

        return sql
