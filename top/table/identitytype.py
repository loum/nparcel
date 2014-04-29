__all__ = [
    "IdentityType",
]
import top


class IdentityType(top.Table):
    """DB identity_type table ORM.
    """

    def __init__(self):
        """
        """
        super(IdentityType, self).__init__('identity_type')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "description CHAR(30)"]
