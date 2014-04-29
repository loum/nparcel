import unittest2
import os

import top


class TestDaemonService(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._recipients = ['loumar@tollgroup.com']
        cls._ds = top.DaemonService(pidfile=None)
        cls._ds.emailer.set_template_base(os.path.join('top',
                                                       'templates'))

    def test_init(self):
        """Intialise a DaemonService object.
        """
        msg = 'Not a top.DaemonService object'
        self.assertIsInstance(self._ds, top.DaemonService, msg)

    def test_alert_failed_processing(self):
        """Test alert comms for a processing error.
        """
        # We don't really test anything here.  But, to check that
        # email alerts are sent set dry to False.
        dry = True

        err_items = ['item 1', 'item 2', 'item 3']
        received = self._ds.send_table(recipients=self._recipients,
                                       table_data=err_items,
                                       dry=dry)
        msg = 'Sent e-mail alert should return True'
        self.assertTrue(received, msg)

    def test_send_email_alert_empty_alerts_list(self):
        """Send email with an empty alerts list.
        """
        dry = True

        alerts = []
        received = self._ds.send_table(self._recipients,
                                       table_data=alerts,
                                       dry=dry)
        msg = 'E-mail alert not sent should return False'
        self.assertFalse(received, msg)

    def test_create_table(self):
        """HTML table creation.
        """
        items = ['item 1', 'item 2', 'item 3']
        received = self._ds.create_table(items)
        fh = open(os.path.join('top',
                               'tests',
                               'files',
                               'proc_err_table.out'))
        expected = fh.read().rstrip()
        fh.close()
        msg = 'HTML table creation error'
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        del cls._recipients
        cls._ds = None
        del cls._ds
