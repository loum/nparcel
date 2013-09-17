__all__ = [
    "Reminder",
]
import time
import datetime
import ConfigParser

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

    """
    def __init__(self, config_file=None, db=None):
        """Nparcel Reminder initialisation.

        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self._notification_delay = 345600
        self._start_date = datetime.datetime(2013, 9, 10, 0, 0, 0)

        self._config = nparcel.Config()
        self._config.set_config_file(config_file)

    @property
    def config(self):
        return self._config

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

    def parse_config(self):
        """Read config items form the Reminder configuration file.

        """
        self.config.parse_config()

        # notification_delay.
        try:
            config_delay = self.config.get('misc', 'notification_delay')
            log.debug('Parsed notification delay: "%s"' % config_delay)
        except ConfigParser.NoOptionError, err:
            log.warn('No configured notification delay')
            config_delay = None

        if config_delay is not None:
            self.set_notification_delay(int(config_delay))

        # start_date.
        try:
            config_start = self.config.get('misc', 'start_date')
            log.debug('Parsed start date: "%s"' % config_start)
        except ConfigParser.NoOptionError, err:
            log.warn('No configured start date')
            config_start = None

        if config_start is not None:
            start_time = time.strptime(config_start, "%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.fromtimestamp(time.mktime(start_time))
            self.set_start_date(dt)

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
        sql = self.db.jobitem.uncollected_sql(self.start_date, threshold_dt)
        self.db(sql)

        for row in self.db.rows():
            yield row[0]

    def process(self, dry=False):
        """Identifies uncollected parcels and sends notifications.

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            list of uncollected job_items that were successfully
            processed

        """
        processed_ids = []

        self.parse_config()
        for id in self.get_uncollected_items():
            log.info('Identified uncollected job_item.id: %d' % id)
            processed_ids.append(id)

        return processed_ids
