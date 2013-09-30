__all__ = [
    "Reminder",
]
import os
import datetime

import nparcel
from nparcel.utils.log import log


class Reminder(object):
    """Nparcel Reminder class.

    .. attribute:: config

        path name to the configuration file

    .. attribute:: notification_delay

        period (in seconds) that triggers a delayed pickup (default is
        345600 seconds or 4 days)

    .. attribute:: start_date

        date when delayed notifications start

    .. attribute:: comms_dir

        directory where comms files are sent for further processing

    """
    _comms_dir = None
    _template_base = None

    def __init__(self,
                 notification_delay=345600,
                 start_date=datetime.datetime(2013, 9, 10, 0, 0, 0),
                 db=None,
                 comms_dir=None):
        """Nparcel Reminder initialisation.

        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self._notification_delay = notification_delay
        self._start_date = start_date

        if comms_dir is not None:
            self.set_comms_dir(comms_dir)

    @property
    def notification_delay(self):
        return self._notification_delay

    def set_notification_delay(self, value):
        self._notification_delay = value

    @property
    def start_date(self):
        return self._start_date

    def set_start_date(self, value):
        self._start_date = value

    @property
    def comms_dir(self):
        return self._comms_dir

    def set_comms_dir(self, value):
        if self._create_dir(value):
            self._comms_dir = value

    @property
    def template_base(self):
        return self._template_base

    def set_template_base(self, value):
        self._template_base = value

    def get_uncollected_items(self):
        """Generator which returns the uncollected job_item.id's.

        **Returns:**
            list of integer values that represent the job_item.id's of
            uncollected parcels.

        """
        job_items = []

        now = datetime.datetime.now()
        delayed_dt = datetime.timedelta(seconds=self.notification_delay)
        threshold_dt = now - delayed_dt
        threshold_dt_str = threshold_dt.strftime('%Y-%m-%d %H:%M:%S')
        sql = self.db.jobitem.uncollected_sql(self.start_date,
                                              threshold_dt_str)
        self.db(sql)

        for row in self.db.rows():
            yield row[0]

    def process(self, dry=False):
        """Identifies uncollected parcels and sends notifications.

        For each uncollected parcel (``job_item.id``), details such as
        Agent information, contact mobile and email and created timestamp
        are extracted from the database.

        A reminder message will be send to the customer if a valid mobile
        and/or email address is found.

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            list of uncollected job_items that were successfully
            processed

        """
        processed_ids = []

        for id in self.get_uncollected_items():
            comms_file = "%d.%s" % (id, 'rem')
            abs_comms_file = os.path.join(self.comms_dir, comms_file)
            log.info('Writing Reminder comms file to "%s"' % abs_comms_file)
            try:
                fh = open(abs_comms_file, 'w')
                fh.close()
            except IOError, err:
                log.error('Unable to open comms file %s: %s' %
                          (abs_comms_file, err))

            processed_ids.append(id)

        return processed_ids

    def _create_dir(self, dir):
        """Helper method to manage the creation of a directory.

        **Args:**
            dir: the name of the directory structure to create.

        **Returns:**
            boolean ``True`` if directory exists.

            boolean ``False`` if the directory does not exist and the
            attempt to create it fails.

        """
        status = True

        # Attempt to create the directory if it does not exist.
        if dir is not None and not os.path.exists(dir):
            try:
                log.info('Creating directory "%s"' % dir)
                os.makedirs(dir)
            except OSError, err:
                status = False
                log.error('Unable to create directory "%s": %s"' %
                          (dir, err))

        return status
