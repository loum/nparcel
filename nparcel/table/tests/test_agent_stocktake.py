import unittest2
import os

import nparcel


class TestAgentStocktake(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._st = nparcel.AgentStocktake()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        cls._db.create_table(name='agent_stocktake',
                             schema=cls._db.agent_stocktake.schema)
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
        expected = [('TEST_REF_NOT_PROC',)]
        msg = 'Reference-based agent_stocktake query error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._st = None
