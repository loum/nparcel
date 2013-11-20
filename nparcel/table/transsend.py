__all__ = [
    "TransSend"
]
import nparcel


class TransSend(nparcel.Table):
    """TransSend DB transsend table ORM.
    """

    def __init__(self):
        """transsend table initialiser.
        """
        super(TransSend, self).__init__('v_nparcel_adp_connotes')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "connote_number TEXT(32)",
                "transsend_job_number TEXT(16)",
                "item_number TEXT(32)",
                "latest_scan_event_action TEXT(64) NOT NULL",
                "job_due_date TIMESTAMP",
                "job_last_updated_date TIMESTAMP",
                "job_type TEXT(64)",
                "job_status TEXT(64)"]

    def connote_sql(self, connote_nbr):
        """SQL wrapper to extract the collected items from the "jobitems"
        table.

        **Args:**
            *connote*: Connote value relating to the
            ``job_item.connote_nbr`` column

        **Returns:**
            the SQL string

        """
        sql = """SELECT *
FROM %s
WHERE connote_number = '%s'""" % (self.name, connote_nbr)

        return sql
