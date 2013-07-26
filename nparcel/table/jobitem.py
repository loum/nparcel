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
        super(JobItem, self).__init__('job_item')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "job_id INTEGER",
                "connote_nbr CHAR(30)",
                "consumer_name CHAR(30)",
                "pieces INTEGER",
                "status INTEGER",
                "created_ts TIMESTAMP"]
