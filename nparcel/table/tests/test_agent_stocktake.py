import unittest2
import os
import datetime

import nparcel


class TestAgentStocktake(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._st = nparcel.AgentStocktake()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        db = cls._db
        fixture_dir = os.path.join('nparcel',
                                   'tests',
                                   'fixtures')
        fixtures = [{'db': db.agent_stocktake,
                     'fixture': 'agent_stocktakes.py'},
                    {'db': db.agent,
                     'fixture': 'agents.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

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
                    ('JOB_TEST_REF_NOT_PROC_PCKD_UP',),
                    ('TEST_REF_NOT_PROC_PCKD_UP',)]
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
                    ('JOB_TEST_REF_NOT_PROC_PCKD_UP',),
                    ('TEST_REF_NOT_PROC_PCKD_UP',)]
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
        oldest = self._now - datetime.timedelta(12)

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
        expected = [('NROS010', 'N031', 'N031 Name', '%s' % str(old_date))]
        msg = 'Compliance agent_stocktake query error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._db.rollback()

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._st = None
