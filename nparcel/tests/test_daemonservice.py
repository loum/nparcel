import unittest2
import os

import nparcel


class TestDaemonService(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._recipients = ['loumar@tollgroup.com']
        cls._ds = nparcel.DaemonService(pidfile=None)
        cls._ds.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))

    def test_init(self):
        """Intialise a DaemonService object.
        """
        msg = 'Not a nparcel.DaemonService object'
        self.assertIsInstance(self._ds, nparcel.DaemonService, msg)

    def test_alert_failed_processing(self):
        """Test alert comms for a processing error.
        """
        # We don't really test anything here.  But, to check that
        # email alerts are sent set dry to False.
        dry = True

        err_file = 'err.txt'
        fh = open('nparcel/tests/files/proc_err_table.out')
        err_table = fh.read().rstrip()
        fh.close()
        data = {'file': err_file,
                'facility': 'facility',
                'err_table': err_table}

        self._ds.emailer.send_comms(template='proc_err',
                                    data=data,
                                    recipients=self._recipients,
                                    dry=dry)

    def test_create_table(self):
        """HTML table creation.
        """
        items = ['item 1', 'item 2', 'item 3']
        received = self._ds.create_table(items)
        fh = open('nparcel/tests/files/proc_err_table.out')
        expected = fh.read().rstrip()
        fh.close()
        msg = 'HTML table creation error'
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        del cls._recipients
        cls._ds = None
        del cls._ds
