__all__ = [
    "RemindDaemon",
]
import time
import signal

import nparcel


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
