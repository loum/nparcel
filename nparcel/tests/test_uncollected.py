import unittest2
import os
import datetime

import nparcel


class TestUncollected(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._u = nparcel.Uncollected()
        db = cls._u.db
        db.create_table(name='agent_stocktake',
                        schema=db.agent_stocktake.schema)

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
WHERE id IN (20, 22)""" % cls._now
        db(sql)

        db.commit()

    def test_init(self):
        """Initialise a Uncollected object.
        """
        msg = 'Object is not an nparcel.Uncollected'
        self.assertIsInstance(self._u, nparcel.Uncollected, msg)

    def test_process_dry_run(self):
        """Check uncollected aged parcel processing -- dry run.
        """
        dry = True

        received = self._u.process(dry=dry)
        expected = [(20,
                     1,
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
                     'VIC Test Newsagent 999'),
                    (22,
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
                     'VIC Test Newsagent 999')]
        msg = 'List of uncollected job_item IDs incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    @classmethod
    def tearDownClass(cls):
        cls._u = None
        del cls._u
