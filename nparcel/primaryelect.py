__all__ = [
    "PrimaryElect",
]
import nparcel
from nparcel.utils.log import log


class PrimaryElect(nparcel.Service):
    """Nparcel PrimaryElect class.

    """
    def __init__(self, db=None, comms_dir=None):
        """Nparcel PrimaryElect initialisation.

        """
        super(nparcel.PrimaryElect, self).__init__(db=db,
                                                   comms_dir=comms_dir)

    def get_primary_elect_job_item_id(self, connote):
        """Return ``jobitem.id`` whose connote is associated with a
        ``job`` that is defined *Primary Elect* (``job.service_code`` = 3).

        """
        ids = []
        sql = self.db.jobitem.connote_base_primary_elect_job(connote)
        self.db(sql)
        for row in self.db.rows():
            ids.append(row[0])

        return ids

    def process(self, connotes=None, dry=False):
        """Identifies primary elects jobs based on job_item connote value.

        For each uncollected parcel (``job_item.id``), details such as
        Agent information, contact mobile and email and created timestamp
        are extracted from the database.

        Should the primary elect job_item feature an email and/or mobile
        number then notifications will be sent.

        **Kwargs:**
            *connotes*: list of connotes to process

            *dry*: only report, do not execute

        **Returns:**
            list of primary elect job_items for whom notifications were
            successfully processed.  Successful represents whether a comms
            for email *and* SMS was produced.

        """
        processed_ids = []

        if connotes is None:
            connotes = []

        for connote in connotes:
            log.info('Checking primary elect connote: "%s"' % connote)
            for id in self.get_primary_elect_job_item_id(connote):
                log.info('Preparing comms flag for job_item.id: %d' % id)
                if (self.flag_comms('email', id, 'pe') and
                    self.flag_comms('sms', id, 'pe')):
                    processed_ids.append(id)
                else:
                    log.error('Comms flag error for job_item.id: %d' % id)

        return processed_ids
