import unittest2
import datetime

import nparcel


class TestAuditer(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()
        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}
        cls._a = nparcel.Auditer(bu_ids=bu_ids)

    def test_init(self):
        """Initialise a Auditer object.
        """
        msg = 'Object is not an nparcel.Auditer'
        self.assertIsInstance(self._a, nparcel.Auditer, msg)

    def test_translate_bu(self):
        """Translate BU ID to Business Unit name.
        """
        headers = ['JOB_ITEM_ID',
                   'JOB_BU_ID',
                   'CONNOTE_NBR',
                   'BARCODE',
                   'ITEM_NBR',
                   'JOB_TS',
                   'CREATED_TS',
                   'NOTIFY_TS',
                   'PICKUP_TS',
                   'PIECES',
                   'CONSUMER_NAME',
                   'DP_CODE',
                   'AGENT_NAME']
        row = (22,
               1,
               'ARTZ061184',
               'JOB_TEST_REF_NOT_PROC_PCKD_UP',
               '00393403250082030048',
               '%s' % self._now,
               '%s' % self._now,
               None,
               None,
               22,
               'Con Sumertwentytwo',
               'VIC999',
               'VIC Test Newsagent 999')
        received = self._a._translate_bu(headers, row, self._a.bu_ids)
        expected = (22,
                    'Toll Priority',
                    'ARTZ061184',
                    'JOB_TEST_REF_NOT_PROC_PCKD_UP',
                    '00393403250082030048',
                    '%s' % self._now,
                    '%s' % self._now,
                    None,
                    None,
                    22,
                    'Con Sumertwentytwo',
                    'VIC999',
                    'VIC Test Newsagent 999')

        msg = 'Translated tuple error'
        self.assertTupleEqual(received, expected, msg)

    def test_translate_bu_no_bu_ids(self):
        """Translate BU ID to Business Unit name -- no BU IDs defined
        """
        old_bu_ids = self._a.bu_ids
        self._a.set_bu_ids({})

        headers = ['JOB_ITEM_ID',
                   'JOB_BU_ID',
                   'CONNOTE_NBR',
                   'BARCODE',
                   'ITEM_NBR',
                   'JOB_TS',
                   'CREATED_TS',
                   'NOTIFY_TS',
                   'PICKUP_TS',
                   'PIECES',
                   'CONSUMER_NAME',
                   'DP_CODE',
                   'AGENT_NAME']
        row = (22,
               1,
               'ARTZ061184',
               'JOB_TEST_REF_NOT_PROC_PCKD_UP',
               '00393403250082030048',
               '%s' % self._now,
               '%s' % self._now,
               None,
               None,
               22,
               'Con Sumertwentytwo',
               'VIC999',
               'VIC Test Newsagent 999')
        received = self._a._translate_bu(headers, row, self._a.bu_ids)
        expected = (22,
                    1,
                    'ARTZ061184',
                    'JOB_TEST_REF_NOT_PROC_PCKD_UP',
                    '00393403250082030048',
                    '%s' % self._now,
                    '%s' % self._now,
                    None,
                    None,
                    22,
                    'Con Sumertwentytwo',
                    'VIC999',
                    'VIC Test Newsagent 999')

        msg = 'Translated tuple error'
        self.assertTupleEqual(received, expected, msg)

        # Clean up.
        self._a.set_bu_ids(old_bu_ids)

    def test_translate_bu_no_job_bu_id(self):
        """Translate BU ID to Business Unit name -- no JOB_BU_ID
        """
        headers = ['JOB_ITEM_ID',
                   'CONNOTE_NBR',
                   'BARCODE',
                   'ITEM_NBR',
                   'JOB_TS',
                   'CREATED_TS',
                   'NOTIFY_TS',
                   'PICKUP_TS',
                   'PIECES',
                   'CONSUMER_NAME',
                   'DP_CODE',
                   'AGENT_NAME']
        row = (22,
               'ARTZ061184',
               'JOB_TEST_REF_NOT_PROC_PCKD_UP',
               '00393403250082030048',
               '%s' % self._now,
               '%s' % self._now,
               None,
               None,
               22,
               'Con Sumertwentytwo',
               'VIC999',
               'VIC Test Newsagent 999')
        received = self._a._translate_bu(headers, row, self._a.bu_ids)
        expected = (22,
                    'ARTZ061184',
                    'JOB_TEST_REF_NOT_PROC_PCKD_UP',
                    '00393403250082030048',
                    '%s' % self._now,
                    '%s' % self._now,
                    None,
                    None,
                    22,
                    'Con Sumertwentytwo',
                    'VIC999',
                    'VIC Test Newsagent 999')

        msg = 'Translated tuple error'
        self.assertTupleEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._now = None
        del cls._now
        cls._a = None
        del cls._a
