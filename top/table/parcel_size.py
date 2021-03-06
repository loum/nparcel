__all__ = [
    "ParcelSize",
]
import top


class ParcelSize(top.Table):
    """Toll Outlet Portal DB parcel_size table ORM.
    """
    def __init__(self):
        """
        """
        super(ParcelSize, self).__init__(name='parcel_size')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "code TEXT(5)",
                "description TEXT(40)"]
