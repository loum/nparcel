import unittest2

import nparcel


class TestAgent(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._agent = nparcel.Agent()
        cls._db = nparcel.DbSession()
        cls._db.connect()
        cls._db.create_table(name="agent",
                             schema=cls._agent.schema)
 
    def test_init(self):
        """Placeholder test to make sure the Agent table is created.
        """
        pass

    def test_check_agent_id(self):
        """Agent ID table check.
        """
        a_id = 'N014'
        sql = """
INSERT INTO agent (code)
VALUES ("%s")""" % a_id
        self._db(sql)

        self._db(self._agent.check_agent_id(agent_id=a_id))
        received = []
        for row in self._db.rows():
            received.append(row[0])
        expected = [1]
        msg = 'Agent ID value not returned from the "agent" table'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
