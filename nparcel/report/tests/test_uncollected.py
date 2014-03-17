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
        cls._u.set_delivery_partners(['Nparcel'])
        db = cls._u.db

        # Prepare some sample data.
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.agent_stocktake,
                     'fixture': 'agent_stocktakes.py'},
                    {'db': db.agent,
                     'fixture': 'agents.py'},
                    {'db': db.delivery_partner,
                     'fixture': 'delivery_partners.py'},
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
WHERE id IN (20, 22)""" % cls._now
        db(sql)

        # "job_item" table timestamp updates.
        cls._old_created_ts = cls._now - datetime.timedelta(99)
        sql = """UPDATE job_item
SET created_ts = '%s'
WHERE id IN (15, 16, 19)""" % cls._old_created_ts
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
                     '="TEST_REF_001"',
                     '="aged_parcel_unmatched"',
                     '="aged_connote_match"',
                     '="%s"' % str(self._now).split('.', 1)[0],
                     '="%s"' % str(self._old_created_ts).split('.', 1)[0],
                     '',
                     '',
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
                     'VIC999',
                     'V999',
                     'VIC Test Newsagent 999',
                     0),
                    (16,
                     'Toll Priority',
                     '="aged_item_match"',
                     '="aged_parcel_unmatched"',
                     '="TEST_REF_001"',
                     '="%s"' % str(self._now).split('.', 1)[0],
                     '="%s"' % str(self._old_created_ts).split('.', 1)[0],
                     '',
                     '',
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
                     'VIC999',
                     'V999',
                     'VIC Test Newsagent 999',
                     0),
                    (19,
                     'Toll Priority',
                     '="ARTZ061184"',
                     '="TEST_REF_001"',
                     '="00393403250082030046"',
                     '="%s"' % str(self._now).split('.', 1)[0],
                     '="%s"' % str(self._old_created_ts).split('.', 1)[0],
                     '',
                     '',
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
                     'VIC999',
                     'V999',
                     'VIC Test Newsagent 999',
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
                    'ST_DP_CODE',
                    'ST_AGENT_CODE',
                    'ST_AGENT_NAME',
                    'DELTA_TIME']
        msg = 'Headers after DELTA_TIME addition error'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._u = None
        del cls._u
        cls._now = None
        del cls._now
        cls._old_created_ts = None
        del cls._old_created_ts
