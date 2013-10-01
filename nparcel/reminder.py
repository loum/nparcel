__all__ = [
    "Reminder",
]
import os
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
            processed

        """
        processed_ids = []

        for id in self.get_uncollected_items():
            comms_file = "%d.%s" % (id, 'rem')
            abs_comms_file = os.path.join(self.comms_dir, comms_file)
            log.info('Writing Reminder comms file to "%s"' % abs_comms_file)
            try:
                fh = open(abs_comms_file, 'w')
                fh.close()
                processed_ids.append(id)
            except IOError, err:
                log.error('Unable to open comms file %s: %s' %
                          (abs_comms_file, err))

        return processed_ids
