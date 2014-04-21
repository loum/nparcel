__all__ = [
    "ReminderB2CConfig",
]
import sys
import time
import datetime
import ConfigParser

import nparcel
from nparcel.utils.log import log


class ReminderB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.ReminderB2CConfig` captures the configuration items
    required for the ``npreminderd`` facility.

    .. attribute:: reminder_loop

        time (seconds) between reminder processing iterations.

    .. attribute:: notification_delay

        period (in seconds) that triggers a reminder notice

    .. attribute:: start_date

        ignores records whose job_item.created_ts occurs before this date

    .. attribute:: hold_period

        defines the time period (in seconds) since the job_item.created_ts
        that the agent will hold the parcel before being returned

    """
    _reminder_loop = 300
    _notification_delay = 345600
    _start_date = datetime.datetime(2013, 10, 9, 0, 0, 0)
    _hold_period = 691200

    @property
    def reminder_loop(self):
        return self._reminder_loop

    def set_reminder_loop(self, value):
        self._reminder_loop = int(value)
        log.debug('%s reminder_loop set to %d' %
                  (self.facility, self.reminder_loop))

    @property
    def notification_delay(self):
        return self._notification_delay

    def set_notification_delay(self, value):
        self._notification_delay = int(value)
        log.debug('%s notification_delay set to %d' %
                  (self.facility, self.notification_delay))

    @property
    def start_date(self):
        return self._start_date

    def set_start_date(self, value):
        self._start_date = value
        log.debug('%s start_date set to "%s"' %
                  (self.facility, self.start_date))

    @property
    def hold_period(self):
        return self._hold_period

    def set_hold_period(self, value):
        self._hold_period = int(value)
        log.debug('%s hold_period set to %s' %
                  (self.facility, self.hold_period))

    def __init__(self, file=None):
        """:class:`nparcel.ReminderB2CConfig` initialisation.
        """
        nparcel.B2CConfig.__init__(self, file)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        try:
            self.set_comms_dir(self.get('dirs', 'comms'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s dirs.comms is a required item: %s' %
                         (self.facility, err))
            sys.exit(1)

        # Reminder specific.
        try:
            self.set_reminder_loop(self.get('timeout', 'reminder_loop'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s timeout.reminder_loop: %s, Using %d' %
                      (self.facility, err, self.reminder_loop))

        try:
            tmp = self.get('reminder', 'notification_delay')
            self.set_notification_delay(tmp)
        except ConfigParser.NoOptionError, err:
            log.debug('%s reminder.notification_delay: %s. Using %d' %
                      (self.facility, err, self.notification_delay))

        try:
            start_date = self.get('reminder', 'start_date')
            start_time = time.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.fromtimestamp(time.mktime(start_time))
            self.set_start_date(dt)
        except ConfigParser.NoOptionError, err:
            log.debug('%s reminder.start_date: %s. Using "%s"' %
                      (self.facility, err, self.start_date))

        try:
            tmp = self.get('reminder', 'hold_period')
            self.set_hold_period(tmp)
        except ConfigParser.NoOptionError, err:
            log.debug('%s reminder.hold_period: %s. Using %s' %
                      (self.facility, err, self.hold_period))
