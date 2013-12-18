import unittest2
import os
import datetime

import nparcel


class TestTotals(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()
        cls.maxDiff = None

        cls._c = nparcel.Totals()
        db = cls._c.db

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
        """Initialise a Totals object.
        """
        msg = 'Object is not an nparcel.Totals'
        self.assertIsInstance(self._c, nparcel.Totals, msg)

    def test_process(self):
        """Check totals processing.
        """
        ids = (1, 2, 3)
        received = self._c.process(id=ids)
        expected = [('VIC999', 'V999', 'VIC Test Newsagent 999', 92, 127)]
        msg = 'List of parcel counts incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

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
