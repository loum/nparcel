import unittest2

import nparcel


class TestAgent(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._agent = nparcel.Agent()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        # Load a single record.
        name = 'Auburn Newsagency'
        address = '119 Auburn Road'
        suburb = 'HAWTHORN EAST'
        postcode = '3123'
        sql = """INSERT INTO agent (name, address, suburb, postcode)
VALUES ('%s', '%s', '%s', '%s')""" % (name, address, suburb, postcode)
        cls._test_id = cls._db.insert(sql)

    def test_init(self):
        """Placeholder test to make sure the Agent table is created.
        """
        msg = 'Object is not an nparcel.Agent'
        self.assertIsInstance(self._agent, nparcel.Agent, msg)

    def test_check_agent_id(self):
        """Agent ID table check.
        """
        a_code = 'N014'
        sql = """INSERT INTO agent (code)
VALUES ("%s")""" % a_code
        self._db(sql)

        self._db(self._agent.check_agent_id(agent_code=a_code))
        received = []
        for row in self._db.rows():
            received.append(row[0])
        expected = [2]
        msg = 'Agent ID value not returned from the "agent" table'
        self.assertListEqual(received, expected, msg)

        # Restore DB state.
        self._db.connection.rollback()

    def test_check_agent(self):
        """Agent details check.
        """
        self._db(self._agent.agent_sql(id=self._test_id))
        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [('Auburn Newsagency',
                     '119 Auburn Road',
                     'HAWTHORN EAST',
                     '3123')]
        msg = 'Agent details not as expected'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
        cls._test_id = None
