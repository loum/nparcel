import unittest2
import os

import nparcel


class TestAgent(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._agent = nparcel.Agent()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')

        db = cls._db
        fixtures = [{'db': db.agent, 'fixture': 'agents.py'},
                    {'db': db.parcel_size, 'fixture': 'parcel_sizes.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Placeholder test to make sure the Agent table is created.
        """
        msg = 'Object is not an nparcel.Agent'
        self.assertIsInstance(self._agent, nparcel.Agent, msg)

    def test_check_agent_id(self):
        """Agent ID table check.
        """
        a_code = 'W049'

        self._db(self._agent.check_agent_id(agent_code=a_code))
        received = list(self._db.rows())
        expected = [(5,)]
        msg = 'Agent ID value not returned from the "agent" table'
        self.assertListEqual(received, expected, msg)

        # Restore DB state.
        self._db.connection.rollback()

    def test_check_agent(self):
        """Agent details check.
        """
        self._db(self._agent.agent_sql(id=4))
        received = list(self._db.rows())
        expected = [('George Street News',
                     '370 George Street',
                     'Brisbane',
                     '4000')]
        msg = 'Agent details not as expected'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._agent = None
        cls._test_id = None
