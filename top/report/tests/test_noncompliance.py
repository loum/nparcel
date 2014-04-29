import unittest2
import os
import datetime

import top


class TestNonCompliance(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()
        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}

        cls.maxDiff = None

        cls._c = top.NonCompliance(bu_ids=bu_ids,
                                   delivery_partners=['Nparcel'])
        db = cls._c.db

        # Prepare some sample data.
        fixture_dir = os.path.join('top', 'tests', 'fixtures')
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
WHERE id IN (15, 16, 19, 20, 22)""" % cls._now
        db(sql)

        cls._old_date = cls._now - datetime.timedelta(8)
        cls._older_date = cls._now - datetime.timedelta(10)

        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE id IN (6)""" % cls._old_date
        db(sql)

        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE id IN (7, 8)""" % cls._older_date
        db(sql)

        db.commit()

    def test_init(self):
        """Initialise a NonCompliance object.
        """
        msg = 'Object is not an top.NonCompliance'
        self.assertIsInstance(self._c, top.NonCompliance, msg)

    def test_process(self):
        """Check compliance processing.
        """
        received = [x[0] for x in list(self._c.process())]
        expected = [2, 3, 4, 6, 8, 9, 10, 11, 12, 13, 14, 17, 18, 23, 24]
        msg = 'List of non-compliant job_items incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_process_no_bu_ids(self):
        """Check compliance processing.
        """
        old_bu_ids = self._c.bu_ids
        self._c.set_bu_ids({})

        received = [x[0] for x in list(self._c.process())]
        expected = []
        msg = 'List of non-compliant job_items incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._c.set_bu_ids(old_bu_ids)

    @classmethod
    def tearDownClass(cls):
        cls._c = None
        del cls._c
        cls._now = None
        del cls._now
        cls._old_date = None
        del cls._old_date
        cls._older_date = None
        del cls._older_date
