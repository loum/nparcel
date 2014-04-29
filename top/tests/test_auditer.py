import unittest2
import datetime
import os

import top


class TestAuditer(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()
        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}
        cls._a = top.Auditer(bu_ids=bu_ids)
        db = cls._a.db

        # Prepare some sample data.
        fixture_dir = os.path.join('top', 'tests', 'fixtures')
        fixtures = [{'db': db.agent_stocktake,
                     'fixture': 'agent_stocktakes.py'}]

        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        cls._agent_stocktake_created_ts = cls._now - datetime.timedelta(6)
        sql = """UPDATE agent_stocktake
 SET created_ts = '%s'
 WHERE reference_nbr = '%s'""" % (cls._agent_stocktake_created_ts,
                                  'TEST_REF_NOT_PROC_PCKD_UP')
        db(sql)

        db.commit()

    def test_init(self):
        """Initialise a Auditer object.
        """
        msg = 'Object is not an top.Auditer'
        self.assertIsInstance(self._a, top.Auditer, msg)

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
        received = self._a.translate_bu(headers, row, self._a.bu_ids)
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
        received = self._a.translate_bu(headers, row, self._a.bu_ids)
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
        received = self._a.translate_bu(headers, row, self._a.bu_ids)
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

    def test_add_date_diff(self):
        """Add date delta to row tuple.
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
        received = self._a.add_date_diff(headers, row)
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
                    'VIC Test Newsagent 999',
                    0)

        msg = 'Date delta tuple error'
        self.assertTupleEqual(received, expected, msg)

    def test_add_date_diff_missing_time_column(self):
        """Add date delta to row tuple -- missing time column.
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
        received = self._a.add_date_diff(headers, row, time_column='xxx')
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
                    'VIC Test Newsagent 999',
                    None)

        msg = 'Date delta tuple error'
        self.assertTupleEqual(received, expected, msg)

    def test_add_date_diff_provide_time(self):
        """Add date delta to row tuple -- time provided.
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
        time_to_compare_dt = datetime.datetime.now()
        time_to_compare_dt += datetime.timedelta(7)
        time_to_compare = time_to_compare_dt.strftime('%Y-%m-%d %H:%M:%S')
        received = self._a.add_date_diff(headers,
                                         row,
                                         time_to_compare=time_to_compare)
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
                    'VIC Test Newsagent 999',
                    7)

        msg = 'Date delta (time provided) tuple error'
        self.assertTupleEqual(received, expected, msg)

    def test_cleanse(self):
        """Cleanse a row.
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
        received = self._a._cleanse(headers, row)
        expected = (22,
                    1,
                    '="ARTZ061184"',
                    '="JOB_TEST_REF_NOT_PROC_PCKD_UP"',
                    '="00393403250082030048"',
                    '="%s"' % str(self._now).split('.', 1)[0],
                    '="%s"' % str(self._now).split('.', 1)[0],
                    '',
                    '',
                    22,
                    'Con Sumertwentytwo',
                    'VIC999',
                    'VIC Test Newsagent 999')

        msg = 'Cleansed tuple error'
        self.assertTupleEqual(received, expected, msg)

    def test_aged_items(self):
        """Test Aged item.
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
               '%s' % (self._now - datetime.timedelta(10)),
               None,
               None,
               22,
               'Con Sumertwentytwo',
               'VIC999',
               'VIC Test Newsagent 999')
        received = self._a.aged_item(headers, row, 'CREATED_TS')
        msg = 'Aged item check (against CREATED_TS) should return True'
        self.assertTrue(received, msg)

        received = self._a.aged_item(headers, row, 'JOB_TS')
        msg = 'Aged item check (against JOB_TS) should return False'
        self.assertFalse(received, msg)

    def test_filter_collected_parcels_not_collected(self):
        """Filter out collected parcels -- not collected.
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
        received = self._a.filter_collected_parcels(headers, row)
        msg = 'Collected parcels filter error -- parcel not collected'
        self.assertFalse(received, msg)

    def test_filter_collected_parcels_collected_after_stocktake(self):
        """Filter out collected parcels -- collected after stocktake.
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
        row = (21,
               1,
               'ARTZ061184',
               'aged_parcel_unmatched',
               'TEST_REF_NOT_PROC_PCKD_UP',
               '%s' % self._now,
               '%s' % self._now,
               '%s' % self._now,
               '%s' % self._now,
               21,
               'Con Sumertwentyone',
               'VIC999',
               'VIC Test Newsagent 999')
        received = self._a.filter_collected_parcels(headers, row)
        msg = 'Collected parcels filter error -- parcel collected after ST'
        self.assertFalse(received, msg)

    def test_filter_collected_parcels_collected_before_stocktake(self):
        """Filter out collected parcels -- collected before stocktake.
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
                   'AGENT_NAME',
                   'STOCKTAKE_CREATED_TS']
        row = (21,
               1,
               'ARTZ061184',
               'aged_parcel_unmatched',
               'TEST_REF_NOT_PROC_PCKD_UP',
               '%s' % self._now,
               '%s' % self._now,
               '%s' % self._now,
               '%s' % (self._now - datetime.timedelta(100)),
               21,
               'Con Sumertwentyone',
               'VIC999',
               'VIC Test Newsagent 999',
               '%s' % self._agent_stocktake_created_ts)
        received = self._a.filter_collected_parcels(headers, row)
        msg = 'Collected parcels filter error -- parcel collected before ST'
        self.assertTrue(received, msg)

    def test_filter_collected_parcels_no_stocktake(self):
        """Filter out collected parcels -- not in stocktake.
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
        row = (21,
               1,
               'banana',
               '',
               '',
               '%s' % self._now,
               '%s' % self._now,
               '%s' % self._now,
               '%s' % (self._now - datetime.timedelta(100)),
               21,
               'Con Sumertwentyone',
               'VIC999',
               'VIC Test Newsagent 999')
        received = self._a.filter_collected_parcels(headers, row)
        msg = 'Collected parcels filter error -- not in stocktake'
        self.assertFalse(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._now = None
        del cls._now
        cls._a = None
        del cls._a
