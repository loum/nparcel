__all__ = [
    "UncollectedDaemon",
]
import nparcel
from nparcel.utils.log import log


class UncollectedDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.Uncollected` class.

    .. attribute:: db_kwargs

        dictionary of connection string values for the Toll Parcel Point
        database.  Typical format is::

            {'driver': ...,
             'host': ...,
             'database': ...,
             'user': ...,
             'password': ...,
             'port': ...}

    """
    _db_kwargs = None

    def __init__(self,
                 pidfile,
                 dry=False,
                 batch=True,
                 config=None):
        super(UncollectedDaemon, self).__init__(pidfile=pidfile,
                                                dry=dry,
                                                batch=batch)

        if config is not None:
            self.config = nparcel.B2CConfig(file=config)
            self.config.parse_config()

        try:
            if self.config.db_kwargs() is not None:
                self.set_db_kwargs(self.config.db_kwargs())
        except AttributeError, err:
            msg = ('DB kwargs not defined in config')
            log.info(msg)

        self._uncollected = nparcel.Uncollected(db_kwargs=self.db_kwargs)

    @property
    def db_kwargs(self):
        return self._db_kwargs

    def set_db_kwargs(self, value):
        if value is not None:
            self._db_kwargs = value

    def _start(self, event):
        """Override the :method:`nparcel.utils.Daemon._start` method.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        while not event.isSet():
            msg = 'Starting stocktake uncollected report ...'
            log.info(msg)

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
