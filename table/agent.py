__all__ = [
    "Agent",
]
import nparcel


class Agent(object):
    """Nparcel DB Agent table ORM.
    """

    def __init__(self):
        """
        """
        self.id = None
        self.code = None

    def check_agent_id(self, agent_id):
        """
        """
        sql = """SELECT id FROM agent WHERE code='%s'""" % agent_id

        return sql

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "code CHAR(6)"]
