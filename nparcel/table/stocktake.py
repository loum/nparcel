__all__ = [
    "AgentParcelStocktake",
]
import nparcel


class AgentParcelStocktake(nparcel.Table):
    """Nparcel DB agent_parcel_stocktake table ORM.
    """

    def __init__(self):
        """
        """
        self._name = 'agent_parcel_stocktake'
        super(AgentParcelStocktake, self).__init__('agent_parcel_stocktake')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "created_ts TIMESTAMP NOT NULL",
                "scanned_item CHAR(30)"]
