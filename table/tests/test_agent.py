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

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None

