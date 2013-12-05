import unittest2
import os
import datetime

import nparcel


class TestUncollectedDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._ud = nparcel.UncollectedDaemon(pidfile=None)
        db = cls._ud._uncollected.db
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
WHERE id IN (15, 16, 19, 20, 22)""" % cls._now
        db(sql)

        db.commit()

    def test_init(self):
        """Intialise a UncollectedDaemon object.
        """
        msg = 'Not a nparcel.UncollectedDaemon object'
        self.assertIsInstance(self._ud, nparcel.UncollectedDaemon, msg)

    @classmethod
    def tearDownClass(cls):
        cls._ud = None
        del cls._ud
        cls._now = None
        del cls._now
