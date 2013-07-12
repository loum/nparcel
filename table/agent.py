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

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "code CHAR(6)"]
