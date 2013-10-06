__all__ = [
    "RemindDaemon",
]
import time
import signal
import datetime

import nparcel
from nparcel.utils.log import log


class ReminderDaemon(nparcel.utils.Daemon):
    """Daemoniser facility for the :class:`nparcel.Remind` class.

    """
    _batch = False

    def __init__(self,
                 pidfile,
                 dry=False,
                 batch=False,
                 config='nparcel.conf'):
        super(ReminderDaemon, self).__init__(pidfile=pidfile)

        self.dry = dry
        self._batch = batch

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

    @property
    def batch(self):
        return self._batch

    def set_batch(self, value):
        self._batch = value

    def _start(self, event):
        """Override the :method:`nparcel.utils.Daemon._start` method.

        Will perform a single iteration in dry and batch modes.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        rem = nparcel.Reminder(db=self.config.db_kwargs(),
                               comms_dir=self.config.comms_dir)

        if self.config.notification_delay is not None:
            rem.set_notification_delay(self.config.notification_delay)
        if self.config.start_date is not None:
            rem.set_start_date(self.config.start_date)
        if self.config.hold_period is not None:
            rem.set_hold_period(self.config.hold_period)

        while not event.isSet():
            if rem.db():
                if not self._skip_day():
                    rem.process(dry=self.dry)
            else:
                log.error('ODBC connection failure -- aborting')
                event.set()
                continue

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config.reminder_loop)

    def _skip_day(self):
        """Check whether comms is configured to skip current day of week.

        **Returns**:
            ``boolean``::

                ``True`` if current day is a skip day
                ``False`` if current day is **NOT** a skip day
        """
        is_skip_day = False

        current_day = datetime.datetime.now().strftime('%A').lower()
        log.debug('Current day is: %s' % current_day.title())

        if current_day in [x.lower() for x in self.config.skip_days]:
            log.info('%s is a configured comms skip day' %
                     current_day.title())
            is_skip_day = True

        return is_skip_day
