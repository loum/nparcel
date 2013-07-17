__all__ = [
    "Reporter",
]
import datetime


class Reporter(object):
    """Nparcel record processing reporter.
    """

    def __init__(self):
        """
        """
        self._failed_log = []
        self.reset()

    def __call__(self, status):
        self.set_total_count()

        if status:
            self.set_good_records()
        else:
            self.set_bad_records()

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

    def reset(self):
        """
        """
        self._failed_log = []
        self._total_count = 0
        self._good_records = 0
        self._bad_records = 0
        self._start_time = datetime.datetime.now()
        self._end_time = None

    @property
    def duration(self):
        """
        """
        return self.end_time - self.start_time

    def end(self):
        """
        """
        self._end_time = datetime.datetime.now()

    def report(self):
        """
        """
        print('Stats:')
        print('------')
        print('Successful count: %d' % self.good_records)
        print('Failure count: %d' % self.bad_records)
        print('Total count: %d' % self.total_count)
        print('Total elapsed time: %s' % self.duration)
        print('Alerts:')
        print('-------')
        for log in self.failed_log:
            print(log)
