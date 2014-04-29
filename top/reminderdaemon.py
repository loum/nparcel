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
        c = None
        if config is not None:
            c = top.ReminderB2CConfig(config)
        top.DaemonService.__init__(self,
                                   pidfile=pidfile,
                                   file=file,
                                   dry=dry,
                                   batch=batch,
                                   config=c)

        try:
            self.set_loop(self.config.reminder_loop)
        except AttributeError, err:
            msg = ('%s loop not in config. Using %d' %
                   (self.facility, self.loop))
            log.debug(msg)

    @property
    def reminder(self):
        return self._reminder

    @property
    def reminder_kwargs(self):
        kwargs = {}
        try:
            kwargs['db'] = self.config.db_kwargs()
        except AttributeError, err:
            log.debug('DB kwargs not in config: %s ' % err)

        try:
            kwargs['comms_dir'] = self.config.comms_dir
        except AttributeError, err:
            log.debug('comms_dir not in config: %s ' % err)

        try:
            if self.config.notification_delay is not None:
                kwargs['notification_delay'] = self.config.notification_delay
        except AttributeError, err:
            log.debug('%s notification_delay not in config: %s' %
                      (self.facility, err))

        try:
            if self.config.start_date is not None:
                kwargs['start_date'] = self.config.start_date
        except AttributeError, err:
            log.debug('%s start_date not in config: %s' %
                      (self.facility, err))

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
