__all__ = [
    "Reminder",
]
import re
import os
import time
import datetime

import nparcel
from nparcel.utils.log import log


class Reminder(object):
    """Nparcel Reminder class.

    .. attribute:: config

        path name to the configuration file

    .. attribute:: notification_delay

        period (in seconds) that triggers a delayed pickup (default is
        345600 seconds or 4 days)

    .. attribute:: start_date

        date when delayed notifications start

    .. attribute:: comms_dir

        directory where comms files are sent for further processing

    """
    _comms_dir = None

    def __init__(self,
                 notification_delay=345600,
                 start_date=datetime.datetime(2013, 9, 10, 0, 0, 0),
                 db=None,
                 proxy=None,
                 scheme='http',
                 sms_api=None,
                 email_api=None,
                 comms_dir=None):
        """Nparcel Reminder initialisation.

        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self._notification_delay = notification_delay
        self._start_date = start_date
        #self._hold_period = hold_period

        if sms_api is None:
            sms_api = {}
        self.smser = nparcel.RestSmser(proxy=proxy,
                                       proxy_scheme=scheme,
                                       **sms_api)

        if email_api is None:
            email_api = {}
        self.emailer = nparcel.RestEmailer(proxy=proxy,
                                           proxy_scheme=scheme,
                                           **email_api)

        if comms_dir is not None:
            self.set_comms_dir(comms_dir)
        self._template_base = None

    @property
    def notification_delay(self):
        return self._notification_delay

    def set_notification_delay(self, value):
        self._notification_delay = value

    @property
    def start_date(self):
        return self._start_date

    def set_start_date(self, value):
        self._start_date = value

    @property
    def comms_dir(self):
        return self._comms_dir

    def set_comms_dir(self, value):
        if self._create_dir(value):
            self._comms_dir = value

    @property
    def template_base(self):
        return self._template_base

    def set_template_base(self, value):
        self._template_base = value

    def get_uncollected_items(self):
        """Generator which returns the uncollected job_item.id's.

        **Returns:**
            list of integer values that represent the job_item.id's of
            uncollected parcels.

        """
        job_items = []

        now = datetime.datetime.now()
        delayed_dt = datetime.timedelta(seconds=self.notification_delay)
        threshold_dt = now - delayed_dt
        threshold_dt_str = threshold_dt.strftime('%Y-%m-%d %H:%M:%S')
        sql = self.db.jobitem.uncollected_sql(self.start_date,
                                              threshold_dt_str)
        self.db(sql)

        for row in self.db.rows():
            yield row[0]

    def process(self, dry=False):
        """Identifies uncollected parcels and sends notifications.

        For each uncollected parcel (``job_item.id``), details such as
        Agent information, contact mobile and email and created timestamp
        are extracted from the database.

        A reminder message will be send to the customer if a valid mobile
        and/or email address is found.

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            list of uncollected job_items that were successfully
            processed

        """
        processed_ids = []

        for id in self.get_uncollected_items():
            for action in ['email', 'sms']:
                comms_file = "%s.%d.%s" % (action, id, 'rem')
                abs_comms_file = os.path.join(self.comms_dir,
                                                  comms_file)
                log.info('Writing Reminder comms file to "%s"' %
                         abs_comms_file)
                try:
                    fh = open(abs_comms_file, 'w')
                    fh.close()
                except IOError, err:
                    log.error('Unable to open comms file %s: %s' %
                              (abs_comms_file, err))
            processed_ids.append(id)

        return processed_ids

    def get_agent_details(self, agent_id):
        """Get agent details.

        **Args:**
            agent_id: as per the agent.id table column

        **Returns:**
            dictionary structure capturing the Agent's details similar to::

                {'name': 'Vermont South Newsagency',
                 'address': 'Shop 13-14; 495 Burwood Highway',
                 'suburb': 'VERMONT',
                 'postcode': '3133',
                 'connote': 'abcd',
                 'item_nbr': '12345678',
                 'created_ts': '2013-09-15 00:00:00'}

        """
        agent_details = []

        sql = self.db.jobitem.job_item_agent_details_sql(agent_id)
        self.db(sql)
        columns = self.db.columns()
        agents = []
        for row in self.db.rows():
            agents.append(row)

        if len(agents) != 1:
            log.error('job_item.id %d agent list: "%s"' %
                      (agent_id, agents))
        else:
            agent_details = [None] * (len(columns) + len(agents[0]))
            agent_details[::2] = columns
            agent_details[1::2] = agents[0]
            log.debug('job_item.id %d detail: "%s"' % (agent_id, agents[0]))

        return dict(zip(agent_details[0::2], agent_details[1::2]))

    def _create_dir(self, dir):
        """Helper method to manage the creation of a directory.

        **Args:**
            dir: the name of the directory structure to create.

        **Returns:**
            boolean ``True`` if directory exists.

            boolean ``False`` if the directory does not exist and the
            attempt to create it fails.

        """
        status = True

        # Attempt to create the directory if it does not exist.
        if dir is not None and not os.path.exists(dir):
            try:
                log.info('Creating directory "%s"' % dir)
                os.makedirs(dir)
            except OSError, err:
                status = False
                log.error('Unable to create directory "%s": %s"' %
                          (dir, err))

        return status
