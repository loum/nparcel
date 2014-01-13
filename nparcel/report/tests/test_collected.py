import unittest2
import os
import datetime

import nparcel


class TestCollected(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls._now = datetime.datetime.now()

        cls._bu_ids = {1: 'Toll Priority',
                       2: 'Toll Fast',
                       3: 'Toll IPEC'}

        cls._u = nparcel.Collected(bu_ids=cls._bu_ids)
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
        cls._early_pickup_ts = cls._now - datetime.timedelta(100)
        sql = """UPDATE job_item
SET created_ts = '%(now)s', pickup_ts = '%(dt)s'
WHERE id IN (21)""" % {'now': cls._now,
                       'dt': cls._early_pickup_ts}
        db(sql)

        db.commit()

    def test_init(self):
        """Initialise a Collected object.
        """
        msg = 'Object is not an nparcel.Collected'
        self.assertIsInstance(self._u, nparcel.Collected, msg)

    def test_process(self):
        """Check collected aged parcel processing.
        """
        id = tuple(self._bu_ids.keys())
        received = self._u.process(id=id)
        expected = [(21,
                     'Toll Priority',
                     '="ARTZ061184"',
                     '="aged_parcel_unmatched"',
                     '="TEST_REF_NOT_PROC_PCKD_UP"',
                     '="%s"' % self._now,
                     '="%s"' % self._now,
                     '',
                     '="%s"' % self._early_pickup_ts,
                     21,
                     'Con Sumertwentyone',
                     'VIC999',
                     'V999',
                     'VIC Test Newsagent 999',
                     '13 Test Street',
                     'Testville',
                     'VIC',
                     '1234',
                     '0431602145')]
        msg = 'List of collected job_item IDs incorrect'
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
                    'AGENT_PHONE_NBR']
        msg = 'Headers after DELTA_TIME addition error'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._u = None
        del cls._u
        cls._now = None
        del cls._now
        cls._early_pickup_ts = None
        del cls._early_pickup_ts
