__all__ = [
    "Agent",
]
import nparcel


class Agent(nparcel.Table):
    """Nparcel DB Agent table ORM.
    """

    def __init__(self):
        """
        """
        self.id = None
        self.code = None
        super(Agent, self).__init__(name='agent')

    def check_agent_id(self, agent_code):
        """SQL wrapper to return return the "agent.id" value for a
        given *agent_code*.

        **Args:**
            agent_code: the Agent Code generally of the form "V001"

        **Returns:**
            the SQL command

        """
        sql = """SELECT id FROM agent WHERE code='%s'""" % agent_code

        return sql

    def agent_sql(self, id):
        """SQL wrapper to return return Agent details of a given *id*.

        **Args:**
            id: the Agent's "agent.id" private key

        **Returns:**
            the SQL command

        """
        sql = """SELECT name, address, suburb, postcode
FROM agent
WHERE id=%d""" % id

        return sql

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "name CHAR(100)",
                "address CHAR(80)",
                "suburb CHAR(30)",
                "state CHAR(3)",
                "postcode CHAR(4)",
                "code CHAR(6)"]
