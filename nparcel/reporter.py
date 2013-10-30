__all__ = [
    "Reporter",
]
import datetime


class Reporter(object):
    """Nparcel record processing reporter.
    """

    def __init__(self, identifier=None):
        """
        """
        self.reset()

        self._identifier = identifier

    def __call__(self, status):
        self.set_total_count()

        if status is None:
            self.set_other_records()
        elif not status:
            self.set_bad_records()
        if status:
            self.set_good_records()

    @property
    def identifier(self):
        return self._identifier

    def set_identifier(self, value):
        self._identifier = value

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
    def other_records(self):
        return self._other_records

    def set_other_records(self):
        self._other_records += 1

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def duration(self):
        duration = 0

        if self.end_time is not None:
            duration = self.end_time - self.start_time

        return duration

    def reset(self, identifier=None):
        """
        """
        self._identifier = identifier
        self._total_count = 0
        self._good_records = 0
        self._bad_records = 0
        self._other_records = 0
        self._start_time = datetime.datetime.now()
        self._end_time = None

    @property
    def end(self):
        self._end_time = datetime.datetime.now()

    def report(self, set_end=True):
        """Dump of current counters.

        **Args:**
            flag to control the reporting end timer

        **Returns:**
            string representation of the various counts.  Similar
            construct is::

                ... success:1 error:1 other:1 total:3 - duration:0

        """
        if set_end:
            self.end

        return('%s success:%d error:%d other:%d total:%d - duration:%s' %
               (str(self.identifier),
                self.good_records,
                self.bad_records,
                self.other_records,
                self.total_count,
                str(self.duration)))
