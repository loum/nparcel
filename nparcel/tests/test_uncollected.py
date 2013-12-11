import unittest2
import os
import datetime

import nparcel


class TestUncollected(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()
        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}

        cls.maxDiff = None

        cls._u = nparcel.Uncollected(bu_ids=bu_ids)
        db = cls._u.db

        # Prepare some sample data.
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.agent_stocktake,
                     'fixture': 'agent_stocktakes.py'},
                    {'db': db.agent,
                     'fixture': 'agents.py'},
                    {'db': db.identity_type,
                     'fixture': 'identity_type.py'},
                    {'db': db.job,
                     'fixture': 'jobs.py'},
                    {'db': db.jobitem,
                     'fixture': 'jobitems.py'}]

        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        # "job" table timestamp updates.
        sql = """UPDATE job
SET job_ts = '%s'""" % cls._now
        db(sql)

        # "job_item" table timestamp updates.
        sql = """UPDATE job_item
SET created_ts = '%s'
WHERE id IN (15, 16, 19, 20, 22)""" % cls._now
        db(sql)

        db.commit()

    def test_init(self):
        """Initialise a Uncollected object.
        """
        msg = 'Object is not an nparcel.Uncollected'
        self.assertIsInstance(self._u, nparcel.Uncollected, msg)

    def test_process(self):
        """Check uncollected aged parcel processing.
        """
        id = 1
        received = self._u.process(id=id)
        expected = [(15,
                     'Toll Priority',
                     'TEST_REF_001',
                     'aged_parcel_unmatched',
                     'aged_connote_match',
                     '%s' % self._now,
                     '%s' % self._now,
                     None,
                     None,
                     15,
                     'Con Sumerfifteen',
                     'VIC999',
                     'V999',
                     'VIC Test Newsagent 999',
                     '13 Test Street',
                     'Testville',
                     'VIC',
                     '1234',
                     '0431602145',
                     0),
                    (16,
                     'Toll Priority',
                     'aged_item_match',
                     'aged_parcel_unmatched',
                     'TEST_REF_001',
                     '%s' % self._now,
                     '%s' % self._now,
                     None,
                     None,
                     16,
                     'Con Sumersixteen',
                     'VIC999',
                     'V999',
                     'VIC Test Newsagent 999',
                     '13 Test Street',
                     'Testville',
                     'VIC',
                     '1234',
                     '0431602145',
                     0),
                    (19,
                     'Toll Priority',
                     'ARTZ061184',
                     'TEST_REF_001',
                     '00393403250082030046',
                     '%s' % self._now,
                     '%s' % self._now,
                     None,
                     None,
                     19,
                     'Con Sumernineteen',
                     'VIC999',
                     'V999',
                     'VIC Test Newsagent 999',
                     '13 Test Street',
                     'Testville',
                     'VIC',
                     '1234',
                     '0431602145',
                     0),
                    (20,
                     'Toll Priority',
                     'TEST_REF_NOT_PROC',
                     'aged_parcel_unmatched',
                     '00393403250082030047',
                     '%s' % self._now,
                     '%s' % self._now,
                     None,
                     None,
                     20,
                     'Con Sumertwenty',
                     'VIC999',
                     'V999',
                     'VIC Test Newsagent 999',
                     '13 Test Street',
                     'Testville',
                     'VIC',
                     '1234',
                     '0431602145',
                     0),
                    (22,
                     'Toll Priority',
                     'ARTZ061184',
                     'JOB_TEST_REF_NOT_PCKD_UP',
                     '00393403250082030048',
                     '%s' % self._now,
                     '%s' % self._now,
                     None,
                     None,
                     22,
                     'Con Sumertwentytwo',
                     'VIC999',
                     'V999',
                     'VIC Test Newsagent 999',
                     '13 Test Street',
                     'Testville',
                     'VIC',
                     '1234',
                     '0431602145',
                     0)]
        msg = 'List of uncollected job_item IDs incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._u.columns
        expected = ['JOB_ITEM_ID',
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
                    'AGENT_CODE',
                    'AGENT_NAME',
                    'AGENT_ADDRESS',
                    'AGENT_SUBURB',
                    'AGENT_STATE',
                    'AGENT_POSTCODE',
                    'AGENT_PHONE_NBR',
                    'DELTA_TIME']
        msg = 'Headers after DELTA_TIME addition error'
        self.assertListEqual(received, expected, msg)

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
        received = self._u._cleanse(headers, row)
        expected = (22,
                    1,
                    '="ARTZ061184"',
                    '="JOB_TEST_REF_NOT_PROC_PCKD_UP"',
                    '="00393403250082030048"',
                    '="%s"' % self._now,
                    '="%s"' % self._now,
                    '',
                    '',
                    22,
                    'Con Sumertwentytwo',
                    'VIC999',
                    'VIC Test Newsagent 999')

        msg = 'Cleansed tuple error'
        self.assertTupleEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._u = None
        del cls._u
        cls._now = None
        del cls._now
