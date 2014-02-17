import unittest2

import nparcel


class TestAdpDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._apdd = nparcel.AdpDaemon(pidfile=None)

    def test_init(self):
        """Initialise a AdpDaemon object.
        """
        msg = 'Not a nparcel.AdpDaemon object'
        self.assertIsInstance(self._apdd, nparcel.AdpDaemon, msg)

    def test_start_dry_loop(self):
        """On Delivery _start dry loop.
        """
        old_dry = self._apdd.dry

        self._apdd.set_dry()
        self._apdd._start(self._apdd.exit_event)

        # Clean up.
        self._apdd.set_dry(old_dry)
        self._apdd._exit_event.clear()

    @classmethod
    def tearDownClass(cls):
        cls._apdd = None
