__all__ = [
    "Reminder",
]
import datetime

import nparcel
from nparcel.utils.log import log


class Reminder(nparcel.Service):
    """Nparcel Reminder class.

    .. attribute:: config

        path name to the configuration file

    .. attribute:: notification_delay

        period (in seconds) that triggers a delayed pickup (default is
        345600 seconds or 4 days)

    .. attribute:: start_date

        date when delayed notifications start

    .. attribute:: hold_period

        period (in seconds) since the ``job_item.created_ts`` that the agent
        will hold the parcel before being returned

    """
    def __init__(self,
                 db=None,
                 comms_dir=None,
                 notification_delay=345600,
                 start_date=datetime.datetime(2013, 9, 10, 0, 0, 0)):
        """Nparcel Reminder initialisation.

        """
        super(nparcel.Reminder, self).__init__(db=db, comms_dir=comms_dir)

        self._notification_delay = notification_delay
        self._start_date = start_date

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
    def hold_period(self):
        return self._hold_period

    def set_hold_period(self, value):
        self._hold_period = value

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

        A reminder message will be flagged if the customer has a valid
        mobile and/or email address.

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            list of uncollected job_items that were successfully
            processed.  Successful represents whether a comms flag for
            email *and* SMS was produced.

        """
        processed_ids = []

        for id in self.get_uncollected_items():
            log.info('Preparing comms flag for job_item.id: %d' % id)
            if (self.flag_comms('email', id, 'rem') and
                self.flag_comms('sms', id, 'rem')):
                processed_ids.append(id)
            else:
                log.error('Comms flag error for job_item.id: %d' % id)

        return processed_ids
