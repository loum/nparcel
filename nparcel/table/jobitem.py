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
                "identity_type_data CHAR(30)"]

    def collected_sql(self, range):
        """SQL wrapper to extract the collected items from the "jobitems"
        table.

        **Args:**
            range: period (in seconds) to search from now

        **Returns:**
            the SQL string

        """
        now = datetime.datetime.now()
        pick_ups_after = now - datetime.timedelta(seconds=range)

        sql = """SELECT %s, %s, %s, %s, %s
FROM %s
WHERE pickup_ts > '%s'""" % ('connote_nbr',
                             'id',
                             'pickup_ts',
                             'pod_name',
                             'identity_type_data',
                             self._name,
                             pick_ups_after)

        return sql
