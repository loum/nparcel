import unittest2
import os

import top


class TestAgent(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._agent = top.Agent()
        cls._db = top.DbSession()
        cls._db.connect()

        fixture_dir = os.path.join('top', 'tests', 'fixtures')

        db = cls._db
        fixtures = [{'db': db.agent, 'fixture': 'agents.py'},
                    {'db': db.parcel_size, 'fixture': 'parcel_sizes.py'},
                    {'db': db.delivery_partner,
                     'fixture': 'delivery_partners.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Placeholder test to make sure the Agent table is created.
        """
        msg = 'Object is not an top.Agent'
        self.assertIsInstance(self._agent, top.Agent, msg)

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

    def test_agent_sql(self):
        """Agent details check.
        """
        self._db(self._agent.agent_sql(id=4))
        received = list(self._db.rows())
        expected = [('George Street News',
                     '370 George Street',
                     'Brisbane',
                     '4000',
                     'Nparcel')]
        msg = 'Agent details not as expected'
        self.assertListEqual(received, expected, msg)

    def test_agent_code_sql(self):
        """Agent code id SQL check.
        """
        self._db(self._agent.agent_code_sql(code='N031'))
        received = list(self._db.rows())
        expected = [(1, )]
        msg = 'Agent code "N031" code not as expected'
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._agent = None
        cls._test_id = None
