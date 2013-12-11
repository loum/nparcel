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
                    ('banana_reference',)]
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
                    ('banana_reference',)]
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
WHERE id IN (6, 9)""" % old_date
        self._db(sql)

        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE id IN (7, 8)""" % older_date
        self._db(sql)

        sql = self._st.compliance_sql()
        self._db(sql)

        received = list(self._db.rows())
        expected = [('QBRI005',
                     'Q013',
                     'George Street News',
                     '%s' % str(old_date)),
                    ('NROS010',
                     'N031',
                     'N031 Name',
                     '%s' % str(old_date))]
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
        expected = [(3,
                     'V999',
                     'TEST_REF_NOT_PROC_PCKD_UP',
                     'VIC999',
                     'VIC Test Newsagent 999'),
                    (5,
                     'V999',
                     'TEST_REF_OLD_DATE',
                     'VIC999',
                     'VIC Test Newsagent 999'),
                    (6,
                     'N031',
                     'AGENT_COMPLIANCE',
                     'NROS010',
                     'N031 Name'),
                    (7,
                     'N031',
                     'AGENT_COMPLIANCE_OLDER',
                     'NROS010',
                     'N031 Name'),
                    (8,
                     'N031',
                     'AGENT_COMPLIANCE_OLDER',
                     'NROS010',
                     'N031 Name'),
                    (9,
                     'Q013',
                     'banana_reference',
                     'QBRI005',
                     'George Street News')]
        msg = 'Reference exception query error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._st = None
