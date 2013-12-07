import unittest2
import os

import nparcel


class TestAgentStocktake(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._st = nparcel.AgentStocktake()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        fixture_file = os.path.join('nparcel',
                                    'tests',
                                    'fixtures',
                                    'agent_stocktakes.py')
        cls._db.load_fixture(cls._db.agent_stocktake, fixture_file)

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

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._st = None
