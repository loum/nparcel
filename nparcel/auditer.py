__all__ = [
    "Auditer",
]
import nparcel


class Auditer(nparcel.Service):
    """Toll Parcel Portal base Auditer class.
    """

    def __init__(self, db_kwargs=None):
        """Auditer initialiser.

        """
        super(nparcel.Auditer, self).__init__(db=db_kwargs)
