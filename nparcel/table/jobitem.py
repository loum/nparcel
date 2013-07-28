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
        super(JobItem, self).__init__('jobitem')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "job_id INTEGER",
                "connote_nbr CHAR(30)",
                "consumer_name CHAR(30)",
                "pieces INTEGER",
                "status INTEGER",
                "created_ts TIMESTAMP",
                "pickup_ts TIMESTAMP"]

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

        sql = """SELECT id
FROM jobitem
WHERE pickup_ts > '%s'""" % pick_ups_after

        return sql
