__all__ = [
    "Reminder",
]
import datetime

import top
from top.utils.log import log


class Reminder(top.Service):
    """Reminder class.

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
    _comms_dir = None
    _notification_delay = 345600
    _hold_period = 345600
    _start_date = datetime.datetime(2013, 10, 9, 0, 0, 0)

    def __init__(self, **kwargs):
        """:class:`top.Reminder` initialisation.

        """
        top.Service.__init__(self,
                             db=kwargs.get('db'),
                             comms_dir=kwargs.get('comms_dir'))

        if kwargs.get('notification_delay') is not None:
            self.set_notification_delay(kwargs.get('notification_delay'))

        if kwargs.get('hold_period') is not None:
            self.set_hold_period(kwargs.get('hold_period'))

        if kwargs.get('start_date') is not None:
            self.set_start_date(kwargs.get('start_date'))

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
            if (self.flag_comms('email', id, 'rem', dry=dry) and
                self.flag_comms('sms', id, 'rem', dry=dry)):
                processed_ids.append(id)
            else:
                log.error('Comms flag error for job_item.id: %d' % id)

        return processed_ids
