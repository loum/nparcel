__all__ = [
    "Job",
]
import nparcel


class Job(nparcel.Table):
    """Nparcel DB Job table ORM.
    """

    def __init__(self):
        """
        """

        self.id = None
        self.card_ref_nbr = None
        super(Job, self).__init__('job')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "bu_id INTEGER",
                "agent_id INTEGER",
                "job_ts TIMESTAMP",
                "card_ref_nbr CHAR(15)",
                "address_1 CHAR(30)",
                "address_2 CHAR(30)",
                "suburb CHAR(30)",
                "postcode CHAR(4)",
                "state CHAR(3)",
                "status INTEGER"]

    def check_barcode(self, barcode):
        """
        """
        sql = """SELECT id, job_ts
FROM job
WHERE card_ref_nbr='%s'
ORDER by job_ts DESC""" % barcode

        return sql

    def update_sql(self, job_id, agent_id_row_id):
        """
        """
        sql = """UPDATE job
SET agent_id=%d
WHERE id=%d""" % (agent_id_row_id, job_id)

        return sql
