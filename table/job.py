__all__ = [
    "Job",
]
import os
import nparcel
from nparcel.utils.log import log


class Job(object):
    """Nparcel DB Job table ORM.
    """

    def __init__(self):
        """
        """

        self.id = None
        self.card_ref_nbr = None

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
        sql = """SELECT id FROM job WHERE card_ref_nbr='%s'""" % barcode

        return sql
