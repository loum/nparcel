__all__ = [
    "ReminderB2CConfig",
]
import time
import datetime
import ConfigParser

import top
from top.utils.log import log
from top.utils.setter import (set_scalar,
                              set_date)


class ReminderB2CConfig(top.B2CConfig):
    """:class:`top.ReminderB2CConfig` captures the configuration items
    required for the ``topreminderd`` facility.

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

    @set_scalar
    def set_reminder_loop(self, value):
        pass

    @property
    def notification_delay(self):
        return self._notification_delay

    @set_scalar
    def set_notification_delay(self, value):
        pass

    @property
    def start_date(self):
        return self._start_date

    @set_date
    def set_start_date(self, value):
        pass

    @property
    def hold_period(self):
        return self._hold_period

    @set_scalar
    def set_hold_period(self, value):
        pass

    def __init__(self, file=None):
        """:class:`top.ReminderB2CConfig` initialisation.
        """
        top.B2CConfig.__init__(self, file)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        top.Config.parse_config(self)

        kwargs = [{'section': 'dirs',
                   'option': 'comms',
                   'var': 'comms_dir',
                   'is_required': True},
                  {'section': 'timeout',
                   'option': 'reminder_loop',
                   'cast_type': 'int'},
                  {'section': 'reminder',
                   'option': 'notification_delay',
                   'cast_type': 'int'},
                  {'section': 'reminder',
                   'option': 'start_date'},
                  {'section': 'reminder',
                   'option': 'hold_period',
                   'cast_type': 'int'}]
        for kw in kwargs:
            self.parse_scalar_config(**kw)
