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

    def check_agent_id(self, agent_id):
        """
        """
        sql = """SELECT id FROM agent WHERE code='%s'""" % agent_id

        return sql

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "code CHAR(6)"]
