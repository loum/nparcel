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

        id = None
        card_ref_nbr = None

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "card_ref_nbr CHAR(15)"]

    def check_barcode(self, barcode):
        """
        """
        sql = """SELECT id FROM job WHERE card_ref_nbr='%s'""" % barcode

        return sql
