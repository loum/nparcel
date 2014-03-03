import unittest2
import os
import datetime

import nparcel


class TestReturns(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._r = nparcel.Returns()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        db = cls._db
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.returns_reference,
                     'fixture': 'returns_reference.py'},
                    {'db': db.returns, 'fixture': 'returns.py'},
                    {'db': db.agent, 'fixture': 'agents.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        # Update the returns created_ts.
        cls._now = str(datetime.datetime.now()).split('.')[0]
        sql = """UPDATE returns
SET created_ts = '%s'""" % cls._now
        db(sql)

        db.commit()

    def test_init(self):
        """Placeholder test to make sure the Returns table is created.
        """
        msg = 'Object is not an nparcel.Returns'
        self.assertIsInstance(self._r, nparcel.Returns, msg)

    def test_extract_id_sql(self):
        """Verify the extract_id_sql string.
        """
        returns_id = 2

        sql = self._db.returns.extract_id_sql(returns_id)
        self._db(sql)

        received = list(self._db.rows())
        expected = [('loumar@tollgroup.com',
                     '0431602145',
                     '%s' % self._now,
                     'Bunters We Never Sleep News + Deli',
                     '693 Albany Hwy',
                     'Victoria Park',
                     '6101',
                     'WA')]
        msg = 'extract_id_sql returned values error'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._r = None
