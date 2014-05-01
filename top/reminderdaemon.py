__all__ = [
    "RemindDaemon",
]
import time
import signal

import top
from top.utils.log import log


class ReminderDaemon(top.DaemonService):
    """Daemoniser facility for the :class:`top.Remind` class.
    """
    _reminder = None

    def __init__(self,
                 pidfile,
                 dry=False,
                 batch=False,
                 config=None):
        top.DaemonService.__init__(self,
                                   pidfile=pidfile,
                                   file=file,
                                   dry=dry,
                                   batch=batch,
                                   config=config)

        if self.config is not None:
            self.set_loop(self.config.reminder_loop)

    @property
    def reminder(self):
        return self._reminder

    @property
    def reminder_kwargs(self):
        kwargs = {}

        kwargs['db'] = self.config.db_kwargs()
        kwargs['comms_dir'] = self.config.comms_dir
        kwargs['notification_delay'] = self.config.notification_delay
        kwargs['hold_period'] = self.config.hold_period
        kwargs['start_date'] = self.config.start_date

        return kwargs

    def _start(self, event):
        """Override the :method:`top.utils.Daemon._start` method.

        Will perform a single iteration in dry and batch modes.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        if self.reminder is None:
            self._reminder = top.Reminder(**(self.reminder_kwargs))

        while not event.isSet():
            if self.reminder.db():
                self.reminder.process(dry=self.dry)
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
                    time.sleep(self.loop)
