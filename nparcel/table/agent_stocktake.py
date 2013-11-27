__all__ = [
    "AgentStocktake",
]
import nparcel


class AgentStocktake(nparcel.Table):
    """AgentStocktake DB table ORM.
    """

    def __init__(self):
        """
        """
        super(AgentStocktake, self).__init__(name='agent_stocktake')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "agent_id INTEGER",
                "created_ts TIMESTAMP",
                "reference_nbr TEXT(32)",
                "processed_ts CHAR(6)"]
