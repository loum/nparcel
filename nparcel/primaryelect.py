__all__ = [
    "PrimaryElect",
]
import nparcel
from nparcel.utils.log import log


class PrimaryElect(nparcel.Reminder):
    """Nparcel PrimaryElect class.

    .. attribute:: template_base

        override the standard location to search for the
        SMS XML template (default is ``~user_home/.nparceld/templates``)

    """
    def __init__(self,
                 db=None,
                 proxy=None,
                 scheme='http',
                 sms_api=None,
                 email_api=None):
        """Nparcel PrimaryElect initialisation.
        """
        super(nparcel.PrimaryElect, self).__init__(db=db,
                                                   proxy=proxy,
                                                   scheme=scheme,
                                                   sms_api=sms_api,
                                                   email_api=email_api)

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
            successfully sent
            processed

        """
        processed_ids = []

        if connotes is None:
            connotes = []

        for connote in connotes:
            log.info('Checking primary elect connote: "%s"' % connote)
            ids = self.get_primary_elect_job_item_id(connote)

            log.debug('Connote "%s" job_item ids %s' % (connote, ids))
            for id in ids:
                template_details = self.get_agent_details(id)
                log.debug('template_details: %s' % template_details)

                email_status = True
                sms_status = True
                email_status = self.send_email(template_details,
                                             template='pe',
                                             err=False,
                                             dry=dry)
                sms_status = self.send_sms(template_details,
                                           template='sms_pe',
                                           dry=dry)

                if not sms_status or not email_status:
                    for addr in self.emailer.support:
                        template_details['email_addr'] = addr
                        email_status = self.send_email(template_details,
                                                       template='pe',
                                                       err=True,
                                                       dry=dry)
                else:
                    processed_ids.append(id)

        return processed_ids
