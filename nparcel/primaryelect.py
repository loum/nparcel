__all__ = [
    "PrimaryElect",
]
import os

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import create_dir


class PrimaryElect(object):
    """Nparcel PrimaryElect class.

    .. attribute:: comms_dir

        directory where comms files are kept for further processing

    """
    _comms_dir = None
    _template_base = None

    def __init__(self, db=None, comms_dir=None):
        """Nparcel PrimaryElect initialisation.

        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        if comms_dir is not None:
            self.set_comms_dir(comms_dir)

    @property
    def comms_dir(self):
        return self._comms_dir

    def set_comms_dir(self, value):
        if create_dir(value):
            self._comms_dir = value

    @property
    def template_base(self):
        return self._template_base

    def set_template_base(self, value):
        self._template_base = value

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
