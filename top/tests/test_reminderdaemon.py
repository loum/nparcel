import unittest2
import os
import datetime
import tempfile

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list)


class TestReminderDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._rd = nparcel.ReminderDaemon(pidfile=None)
        cls._rd._config = nparcel.ReminderB2CConfig()

        cls._comms_dir = tempfile.mkdtemp()
        cls._rd._config.set_comms_dir(cls._comms_dir)

        # Call up front to pre-load the DB.
        cls._rd._reminder = nparcel.Reminder(**(cls._rd.reminder_kwargs))

        db = cls._rd._reminder.db
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.job, 'fixture': 'jobs.py'},
                    {'db': db.jobitem, 'fixture': 'jobitems.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        ts = datetime.datetime.now()
        sql = """UPDATE job_item
SET notify_ts = '%s'
WHERE id = 8""" % str(ts - datetime.timedelta(days=10))
        db(sql)

        db.commit()

    def test_init(self):
        """Intialise a ReminderDaemon object.
        """
        msg = 'Not a nparcel.ReminderDaemon object'
        self.assertIsInstance(self._rd, nparcel.ReminderDaemon, msg)

    def test_start(self):
        """Reminder _start processing dry loop.
        """
        old_dry = self._rd.dry

        self._rd.set_dry()
        self._rd._start(self._rd.exit_event)

        # Clean up.
        self._rd.set_dry(old_dry)
        self._rd.exit_event.clear()

    def test_start_non_dry(self):
        """Start non-dry loop.
        """
        comms_files = ['email.8.rem', 'sms.8.rem']
        dry = False

        old_dry = self._rd.dry
        old_batch = self._rd.batch

        # Start processing.
        self._rd.set_dry(dry)
        self._rd.set_batch()
        self._rd._start(self._rd.exit_event)

        # Check that the reminder comms event files were created.
        comms_dir = self._rd._config.comms_dir
        received = get_directory_files_list(comms_dir)
        expected = [os.path.join(comms_dir, x) for x in comms_files]
        msg = 'List of reminder comms event files not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        remove_files(expected)
        self._rd.set_dry(old_dry)
        self._rd.set_batch(old_batch)
        self._rd.exit_event.clear()

    @classmethod
    def tearDownClass(cls):
        del cls._rd
        os.removedirs(cls._comms_dir)
