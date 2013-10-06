import unittest2

import nparcel


class TestReminderDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf_file = 'nparcel/conf/nparceld.conf'
        cls._rd = nparcel.ReminderDaemon(pidfile=None, config=conf_file)

    def test_init(self):
        """Intialise a ReminderDaemon object.
        """
        msg = 'Not a nparcel.ReminderDaemon object'
        self.assertIsInstance(self._rd, nparcel.ReminderDaemon, msg)

    def test_start(self):
        """Reminder _start processing loop.
        """
        self._rd.dry = True
        self._rd._start(self._rd.exit_event)

    @classmethod
    def tearDownClass(cls):
        cls._rd = None
        del cls._rd
