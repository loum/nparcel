__all__ = [
    "PrimaryElect",
]
import os

import nparcel
from nparcel.utils.log import log


class PrimaryElect(nparcel.Reminder):
    """Nparcel PrimaryElect class.

    .. attribute:: comms_dir

        directory where comms files are kept for further processing

    """
    def __init__(self,
                 db=None,
                 proxy=None,
                 scheme='http',
                 sms_api=None,
                 email_api=None,
                 comms_dir=None):
        """Nparcel PrimaryElect initialisation.
        """
        super(nparcel.PrimaryElect, self).__init__(db=db,
                                                   proxy=proxy,
                                                   scheme=scheme,
                                                   sms_api=sms_api,
                                                   email_api=email_api,
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
            successfully processed

        """
        processed_ids = []

        if connotes is None:
            connotes = []

        for connote in connotes:
            log.info('Checking primary elect connote: "%s"' % connote)
            for id in self.get_primary_elect_job_item_id(connote):
                for action in ['email', 'sms']:
                    comms_file = "%s.%d.%s" % (action, id, 'pe')
                    abs_comms_file = os.path.join(self.comms_dir,
                                                  comms_file)
                    log.info('Writing Primary Elect comms file to "%s"' %
                             abs_comms_file)
                    try:
                        fh = open(abs_comms_file, 'w')
                        fh.close()
                    except IOError, err:
                        log.error('Unable to open comms file %s: %s' %
                                  (abs_comms_file, err))
                processed_ids.append(id)

#            for id in ids:
#                template_details = self.get_agent_details(id)
#                log.debug('template_details: %s' % template_details)
#
#                email_status = True
#                sms_status = True
#                email_status = self.send_email(template_details,
#                                             template='pe',
#                                             err=False,
#                                             dry=dry)
#                sms_status = self.send_sms(template_details,
#                                           template='sms_pe',
#                                           dry=dry)
#
#                if not sms_status or not email_status:
#                    for addr in self.emailer.support:
#                        template_details['email_addr'] = addr
#                        email_status = self.send_email(template_details,
#                                                       template='pe',
#                                                       err=True,
#                                                       dry=dry)
#                else:
#                    log.info('Setting job_item %d notify flag' % id)
#                    if not dry:
#                        self.db(self.db.jobitem.update_notify_ts_sql(id))
#                        self.db.commit()
#                    processed_ids.append(id)

        return processed_ids
