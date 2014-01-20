import unittest2
import os
import datetime

import nparcel


class TestAgentStocktake(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        cls._now = datetime.datetime.now()

        cls._st = nparcel.AgentStocktake()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        db = cls._db
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
WHERE id IN (1, 3, 4, 5, 15, 16, 19, 20, 21, 22)""" % cls._now
        db(sql)

        sql = """UPDATE job_item
SET pickup_ts = '%s'
WHERE id IN (1, 5, 21)""" % cls._now
        db(sql)

        sql = """UPDATE job_item
SET notify_ts = '%s'
WHERE id IN (21)""" % cls._now
        db(sql)

        delayed_dt = cls._now - datetime.timedelta(seconds=(86400 * 5))
        sql = """UPDATE job_item
SET created_ts = '%(dt)s', notify_ts = '%(dt)s'
WHERE id = 2""" % {'dt': delayed_dt}
        db(sql)

        cls._agent_stocktake_created_ts = cls._now - datetime.timedelta(6)
        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE reference_nbr = '%s'""" % (cls._agent_stocktake_created_ts,
                                 'TEST_REF_NOT_PROC_PCKD_UP')
        db(sql)

        db.commit()

    def test_init(self):
        """AgentStocktake table creation.
        """
        msg = 'Object is not an nparcel.AgentStocktake'
        self.assertIsInstance(self._st, nparcel.AgentStocktake, msg)

    def test_reference_sql(self):
        """Verify the reference_sql SQL.
        """
        sql = self._st.reference_sql(alias='banana')
        self._db(sql)

        received = list(self._db.rows())
        expected = [('TEST_REF_001',),
                    ('TEST_REF_NOT_PROC',),
                    ('TEST_REF_NOT_PROC_PCKD_UP',),
                    ('JOB_TEST_REF_NOT_PCKD_UP',),
                    ('banana_reference',),
                    ('agent_exception_ref',)]
        msg = 'Reference-based agent_stocktake query error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_reference_sql_no_alias(self):
        """Verify the reference_sql SQL (no alias).
        """
        sql = self._st.reference_sql()
        self._db(sql)

        received = list(self._db.rows())
        expected = [('TEST_REF_001',),
                    ('TEST_REF_NOT_PROC',),
                    ('TEST_REF_NOT_PROC_PCKD_UP',),
                    ('JOB_TEST_REF_NOT_PCKD_UP',),
                    ('banana_reference',),
                    ('agent_exception_ref',)]
        msg = 'Reference-based agent_stocktake query error (no alias)'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_update_processed_ts_sql(self):
        """Verify the update_processed_ts_sql SQL.
        """
        now = self._db.date_now()
        sql = self._st.update_processed_ts_sql(now)
        self._db(sql)

    def test_compliance_sql(self):
        """Verify the compliance SQL.
        """
        old_date = self._now - datetime.timedelta(8)
        older_date = self._now - datetime.timedelta(10)

        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE id IN (6)""" % old_date
        self._db(sql)

        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE id IN (7, 8)""" % older_date
        self._db(sql)

        sql = self._st.compliance_sql()
        self._db(sql)

        received = list(self._db.rows())
        # Agent BAD1 does not have a reference in the agent_stocktake table.
        # Agent N031 has aged agent_stocktake table entries.
        expected = [('BAD1000',
                     'BAD1',
                     'BAD1 Name',
                     None),
                    ('NROS010',
                     'N031',
                     'N031 Name',
                     '%s' % str(old_date)),
                    ('WVIC005',
                     'W049',
                     'Bunters We Never Sleep News + Deli',
                     None)]
        msg = 'Compliance agent_stocktake query error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._db.rollback()

    def test_reference_exception_sql(self):
        """Verify the reference_exception_sql SQL.
        """
        sql = self._st.reference_exception_sql()
        self._db(sql)

        received = list(self._db.rows())
        expected = [(9,
                     'Q013',
                     'banana_reference',
                     'QBRI005',
                     'George Street News'),
                    (10,
                     'Q013',
                     'agent_exception_ref',
                     'QBRI005',
                     'George Street News')]
        msg = 'Reference exception query error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_stocktake_created_date_single_search_key(self):
        """Verify the stocktake_created_date SQL -- single search key.
        """
        sql = self._st.stocktake_created_date('TEST_REF_NOT_PROC_PCKD_UP')
        self._db(sql)

        received = list(self._db.rows())
        expected = [('%s' % self._agent_stocktake_created_ts,)]
        msg = 'Created date query error - single search key'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_stocktake_created_date_multiple_search_keys(self):
        """Verify the stocktake_created_date SQL - multiple search key.
        """
        sql = self._st.stocktake_created_date('ARTZ061184',
                                              'TEST_REF_NOT_PROC_PCKD_UP')
        self._db(sql)

        received = list(self._db.rows())
        expected = [('%s' % self._agent_stocktake_created_ts,)]
        msg = 'Created date query error - multiple search keys'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._st = None
