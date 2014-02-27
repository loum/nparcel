__all__ = [
    "Returns",
]
import nparcel


class Returns(nparcel.Table):
    """Returnstable ORM.
    """

    def __init__(self):
        """Returns initialiser.
        """
        super(Returns, self).__init__(name='returns')

    @property
    def schema(self):
        return('id INTEGER PRIMARY KEY',
               'agent_id INTEGER',
               'created_ts TIMESTAMP',
               'processed_ts TIMESTAMP',
               'name TEXT(30)',
               'email_addr TEXT(60)',
               'phone_nbr TEXT(12)',
               'receipt_required TEXT(1)')
