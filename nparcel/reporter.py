__all__ = [
    "Reporter",
]
import datetime

from nparcel.utils.log import log


class Reporter(object):
    """Nparcel record processing reporter.
    """

    def __init__(self, identifier=None):
        """
        """
        self._identifier = identifier

        self._failed_log = []
        self.reset()

    def __call__(self, status):
        self.set_total_count()

        if status:
            self.set_good_records()
        else:
            self.set_bad_records()

    @property
    def identifier(self):
        return self._identifier

    @property
    def failed_log(self):
        return self._failed_log

    def set_failed_log(self, logs):
        self._failed_log.extend(logs)

    @property
    def total_count(self):
        return self._total_count

    def set_total_count(self):
        self._total_count += 1

    @property
    def good_records(self):
        return self._good_records

    def set_good_records(self):
        self._good_records += 1

    @property
    def bad_records(self):
        return self._bad_records

    def set_bad_records(self):
        self._bad_records += 1

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def duration(self):
        """
        """
        duration = 0

        if self.end_time is not None:
            duration = self.end_time - self.start_time

        return duration

    def reset(self, identifier=None):
        """
        """
        self._identifier = identifier
        self._failed_log = []
        self._total_count = 0
        self._good_records = 0
        self._bad_records = 0
        self._start_time = datetime.datetime.now()
        self._end_time = None

    def end(self):
        """
        """
        self._end_time = datetime.datetime.now()

    def report(self):
        """
        """
        log_msg = 'success/failed/total:duration'
        if self.identifier is not None:
            log_msg = '%s: %s' % (self.identifier, log_msg)

        return('%s: %d/%d/%d:%s' % (log_msg,
                                    self.good_records,
                                    self.bad_records,
                                    self.total_count,
                                    str(self.duration)))
