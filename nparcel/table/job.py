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
                "job_ts TIMESTAMP NOT NULL",
                "card_ref_nbr CHAR(15)",
                "address_1 CHAR(30)",
                "address_2 CHAR(30)",
                "suburb CHAR(30)",
                "postcode CHAR(4)",
                "state CHAR(3)",
                "status INTEGER",
                "service_code INTEGER"]

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

    def connote_based_job_sql(self, connote):
        """Query job table for records that are related to a job_item
        record with *connote*

        **Args:**
            connote: Conn Note value relating to the job_item.connote_nbr
            column.

        **Returns:**
            the SQL string

        """
        sql = """SELECT j.id
FROM job as j, job_item as ji
WHERE (ji.connote_nbr = '%s' AND j.id = ji.job_id)
ORDER by j.job_ts DESC""" % connote

        return sql

    def item_nbr_based_job_sql(self, item_nbr):
        """Query job table for records that are related to a job_item
        record with *item_nbr*

        **Args:**
            item_nbr: Item Number value relating to the job_item.item_nbr
            column.

        **Returns:**
            the SQL string

        """
        sql = """SELECT j.id
FROM job as j, job_item as ji
WHERE (ji.item_nbr = '%s' AND j.id = ji.job_id)
ORDER by j.job_ts DESC""" % item_nbr

        return sql

    def jobitem_based_job_search_sql(self, connote, item_nbr):
        """Generate SQL that queries the job table for records that are
        related to a job_item record with *connote* and *item_nbr*

        **Args:**
            item_nbr: Item Number value relating to the job_item.item_nbr
            column.

            connote: Conn Note value relating to the job_item.connote_nbr
            column.

        **Returns:**
            the SQL string

        """
        sql = """SELECT j.id
FROM job as j, job_item as ji
WHERE (ji.connote_nbr = '%s' AND
       ji.item_nbr = '%s' AND
       j.id = ji.job_id)
ORDER by j.job_ts DESC""" % (connote, item_nbr)

        return sql

    def postcode_sql(self):
        """Generate SQL that queries the job table for records for the
        postcode and state.

        **Returns:**
            the SQL string

        """
        sql = """SELECT id, postcode, state
FROM %s
WHERE postcode IS NOT NULL and postcode != ''""" % self.name

        return sql

    def update_postcode_sql(self, id, state):
        """Generate SQL that updates the job table for records for the
        postcode and state.

        **Args:**
            *id*: integer value relating to the ``job.id`` to update

            *state*: value to update the ``job.state`` column with

        **Returns:**
            the SQL string

        """
        sql = """UPDATE %s
SET state = '%s'
WHERE id = %d""" % (self.name, state, id)

        return sql

    def reference_sql(self, reference_nbr, period=7, alias='j'):
        """Extract card_ref_nbr number against *reference_nbr*.

        **Args:**
            *reference_nbr*: parcel ID number as scanned by the agent

        **Kwargs:**
            *alias*: table alias (default ``j``)

        **Returns:**
            the SQL string

        """
        sql = """SELECT %(alias)s.id
FROM %(name)s as %(alias)s
WHERE %(alias)s.card_ref_nbr IN (%(ref)s)""" % {'name': self.name,
                                                'ref': reference_nbr,
                                                'alias': alias}

        return sql
