__all__ = [
    "ReturnsReference",
]
import nparcel


class ReturnsReference(nparcel.Table):
    """ReturnsReference table ORM.
    """

    def __init__(self):
        """ReturnsReference initialiser.
        """
        super(ReturnsReference, self).__init__(name='returns_reference')

    @property
    def schema(self):
        return('id INTEGER PRIMARY KEY',
               'returns_id INTEGER',
               'reference_nbr TEXT(32)')
