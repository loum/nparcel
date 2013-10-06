__all__ = [
    "CommsDaemon",
]
import signal
import time
import datetime

import nparcel
from nparcel.utils.log import log


class CommsDaemon(nparcel.utils.Daemon):
    """Daemoniser facility for the :class:`nparcel.Comms` class.

    """
    _batch = False

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config='nparcel.conf'):
        super(CommsDaemon, self).__init__(pidfile=pidfile)

        self.file = file
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

        Will perform a single iteration if the :attr:`file` attribute has
        a list of filenames to process.  Similarly, dry and batch modes
        only cycle through a single iteration.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        comms = nparcel.Comms(db=self.config.db_kwargs(),
                              comms_dir=self.config.comms_dir)

        while not event.isSet():
            files = []

            if comms.db():
                if not self._skip_day():
                    if self._within_time_ranges():
                        if self.file is not None:
                            files.append(self.file)
                            event.set()
                        else:
                            files.extend(comms.get_comms_files())
            else:
                log.error('ODBC connection failure -- aborting')
                event.set()
                continue

            # Start processing files.
            for file in files:
                log.info('Processing file: "%s" ...' % file)
                comms.process(file, self.dry)

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config.comms_loop)

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

    def _within_time_ranges(self):
        """Check whether comms is configured to send comms at current time.

        Expects ranges to be of the format 'HH:MM-HH:MM' otherwise it will
        return ``False`` as no assumptions are made.

        **Returns**:
            ``boolean``::

                ``True`` if current time is within the ranges
                ``False`` if current day is **NOT** within the ranges

        """
        is_within_time_range = True

        current_time = datetime.datetime.now()

        for range in self.config.send_time_ranges:
            log.debug('Checking "%s" is within time range "%s"' %
                      (current_time, range))

            try:
                (lower_str, upper_str) = range.split('-')
            except ValueError, err:
                log.error('Time range "%s" processing error: %s' %
                          (range, err))
                is_within_time_range = False
                break

            lower_str = '%s %s' % (current_time.strftime('%Y-%m-%d'),
                                   lower_str)
            log.debug('Lower date string: %s' % lower_str)
            upper_str = '%s %s' % (current_time.strftime('%Y-%m-%d'),
                                   upper_str)
            log.debug('Upper date string: %s' % upper_str)

            lower_time = time.strptime(lower_str, "%Y-%m-%d %H:%M")
            lower_dt = datetime.datetime.fromtimestamp(time.mktime(lower_time))
            upper_time = time.strptime(upper_str, "%Y-%m-%d %H:%M")
            upper_dt = datetime.datetime.fromtimestamp(time.mktime(upper_time))

            if current_time < lower_dt or current_time > upper_dt:
                is_within_time_range = False
                break

        return is_within_time_range
